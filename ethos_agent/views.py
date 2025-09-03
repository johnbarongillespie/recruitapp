import os
import google.generativeai as genai
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import json
from .models import PromptComponent, Conversation, UserProfile
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.urls import reverse
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# --- Initialization ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro-latest')
# --------------------

@login_required
def index(request):
    logger.info(f"User '{request.user.username}' loaded the agent page.")
    return render(request, 'ethos_agent/index.html')

@login_required
def ask_agent(request):
    if request.method == 'POST':
        # ... (rest of ask_agent logic is the same)
        try:
            core_prompt = PromptComponent.objects.get(name="freya_core_prompt").content
        except PromptComponent.DoesNotExist:
            core_prompt = "You are a helpful AI assistant."
        data = json.loads(request.body)
        user_prompt = data.get('prompt')
        logger.info(f"User '{request.user.username}' submitted a new prompt.")
        history = ""
        recent_conversations = Conversation.objects.filter(user=request.user).order_by('-timestamp')[:5]
        for conv in reversed(recent_conversations):
            history += f"Human: {conv.prompt_text}\nAI: {conv.response_text}\n"
        user_context = f"The user you are speaking to is named {request.user.username}."
        full_prompt = (
            f"{core_prompt}\n\n"
            f"## RECENT CONVERSATION HISTORY\n{history}\n\n"
            f"## USER CONTEXT\n{user_context}\n\n"
            f"## CURRENT USER QUERY\n{user_prompt}"
        )
        try:
            response = model.generate_content(full_prompt)
            ai_response_text = response.text
            logger.info(f"Successfully generated AI response for user '{request.user.username}'.")
            Conversation.objects.create(
                user=request.user,
                prompt_text=user_prompt,
                response_text=ai_response_text
            )
            return JsonResponse({'response': ai_response_text})
        except Exception as e:
            logger.error(f"An API error occurred for user '{request.user.username}': {e}")
            return JsonResponse({'response': f'An error occurred: {e}'})
    return JsonResponse({'response': 'Invalid request.'})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # Deactivate account until email confirmation
            user.save()
            UserProfile.objects.create(user=user)

            # --- Email Verification Logic ---
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = request.build_absolute_uri(
                reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
            )
            
            subject = 'Activate Your Axiomism Agent Account'
            message = f'Hello {user.username},\n\nPlease click the link below to verify your email and activate your account:\n\n{verification_link}\n\nThank you.'
            send_mail(subject, message, 'from@example.com', [user.email])
            
            return HttpResponse("Verification email sent. Please check your email (and the console) to complete registration.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# --- ADD THIS NEW VIEW ---
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