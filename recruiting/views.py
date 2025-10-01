import os
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import json
from .models import PromptComponent, Conversation, UserProfile, ChatSession, PlayerProfile
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

# --- Vertex AI Initialization ---
load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=PROJECT_ID, location=LOCATION)
# Global model initialization has been removed from here.
# ------------------------------------

def landing_page(request):
    return render(request, 'recruiting/landing_page.html')

@login_required
def index(request):
    logger.info(f"User '{request.user.username}' loaded the agent page.")
    return render(request, 'recruiting/index.html')

@login_required
def ask_agent(request):
    if request.method == 'POST':
        # Get the system instruction from the database first.
        try:
            prompt_name = os.getenv('PROMPT_COMPONENT_NAME', 'recruiter_core_prompt')
            core_prompt = PromptComponent.objects.get(name=prompt_name).content
        except PromptComponent.DoesNotExist:
            logger.warning(f"PromptComponent '{prompt_name}' not found. Using fallback.")
            core_prompt = "You are a helpful AI assistant."
        
        # Initialize the model INSIDE the view with the system instruction.
        model = GenerativeModel(
            "gemini-2.5-pro",
            system_instruction=[core_prompt]
        )

        data = json.loads(request.body)
        user_prompt = data.get('prompt')
        session_id = data.get('session_id')
        
        try:
            if session_id:
                chat_session = ChatSession.objects.get(id=session_id, user=request.user)
            else:
                chat_session = ChatSession.objects.create(user=request.user, title=user_prompt[:100])
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Invalid session ID'}, status=404)

        logger.info(f"User '{request.user.username}' submitted a new prompt in session {chat_session.id}.")

        history = []
        recent_conversations = chat_session.messages.order_by('timestamp').all()[:10]
        for conv in recent_conversations:
            history.append({"role": "user", "parts": [{"text": conv.prompt_text}]})
            history.append({"role": "model", "parts": [{"text": conv.response_text}]})
        
        chat = model.start_chat(history=history)

        try:
            # Remove the incorrect 'generation_config' from the send_message call.
            response = chat.send_message(user_prompt)
            ai_response_text = response.text

            Conversation.objects.create(
                session=chat_session,
                user=request.user,
                prompt_text=user_prompt,
                response_text=ai_response_text
            )
            
            return JsonResponse({'response': ai_response_text, 'session_id': chat_session.id})
        except Exception as e:
            logger.error(f"An API error occurred for user '{request.user.username}': {e}")
            return JsonResponse({'response': f'An error occurred: {e}'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def get_chat_sessions(request):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    session_list = [
        {'id': str(session.id), 'title': session.title} 
        for session in sessions
    ]
    return JsonResponse({'sessions': session_list})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            UserProfile.objects.create(user=user)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = request.build_absolute_uri(
                reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
            )
            subject = 'Activate Your RecruitTalk Agent Account'
            message = f'Hello {user.username},\n\nPlease click the link below to verify your email and activate your account:\n\n{verification_link}\n\nThank you.'
            send_mail(subject, message, 'from@example.com', [user.email])
            return HttpResponse("Verification email sent. Please check your email (and the console) to complete registration.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.email_verified = True
        profile.save()
        user.save()
        return redirect('login')
    else:
        return HttpResponse('The verification link is invalid.')