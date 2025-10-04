import os
import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import json
# PlayerProfile is already imported, perfect!
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
from celery.result import AsyncResult
from .tasks import get_ai_response

logger = logging.getLogger(__name__)

# --- Vertex AI Initialization ---
load_dotenv()
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
        data = json.loads(request.body)
        user_prompt = data.get('prompt')
        session_id = data.get('session_id')
        
        try:
            if session_id:
                chat_session = ChatSession.objects.get(id=session_id, user=request.user)
            else:
                chat_session = ChatSession.objects.create(user=request.user, title=user_prompt[:100])
                session_id = chat_session.id
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Invalid session ID'}, status=404)

        # --- MODIFICATION START: Context-Aware Coaching ---
        # Let's give Coach Alex some background on who they're talking to!
        player_context = ""
        try:
            profile = PlayerProfile.objects.select_related('sport').get(user=request.user)
            # We construct a neat little sentence for the AI to understand.
            player_context = (
                f"CONTEXT: You are speaking to an athlete. "
                f"Their profile is: Sport - {profile.sport.name}, "
                f"Position - {profile.position}, "
                f"Graduation Year - {profile.graduation_year}. "
                f"Use this information to personalize your advice."
            )
        except PlayerProfile.DoesNotExist:
            # If there's no profile, no problem. We just proceed without context.
            logger.info(f"No PlayerProfile found for user '{request.user.username}'.")
            pass
        # --- MODIFICATION END ---

        try:
            prompt_name = os.getenv('PROMPT_COMPONENT_NAME', 'recruiter_core_prompt')
            core_prompt_base = PromptComponent.objects.get(name=prompt_name).content
            
            # --- MODIFICATION: Prepend player context to the core prompt ---
            # Voilà! The agent is now instantly aware of the user's profile.
            core_prompt = f"{player_context}\n\n{core_prompt_base}" if player_context else core_prompt_base

        except PromptComponent.DoesNotExist:
            logger.warning(f"PromptComponent '{prompt_name}' not found. Using fallback.")
            core_prompt = "You are a helpful AI assistant."

        history_dicts = []
        recent_conversations = chat_session.messages.select_related('user').order_by('timestamp')[:10]
        for conv in recent_conversations:
            history_dicts.append({"role": "user", "parts": [{"text": conv.prompt_text}]})
            history_dicts.append({"role": "model", "parts": [{"text": conv.response_text}]})
        
        task = get_ai_response.delay(
            user_prompt, 
            core_prompt, 
            history_dicts, 
            str(session_id), 
            request.user.id
        )
        
        return JsonResponse({'task_id': task.id, 'session_id': session_id})

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def get_task_status(request, task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.status == 'SUCCESS' else None,
    }
    return JsonResponse(result)

@login_required
def get_chat_sessions(request):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    session_list = [
        {'id': str(session.id), 'title': session.title} 
        for session in sessions
    ]
    return JsonResponse({'sessions': session_list})

# ... (register and verify_email functions remain unchanged) ...
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            UserProfile.objects.create(user=user)
            # ... rest of the function is unchanged
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