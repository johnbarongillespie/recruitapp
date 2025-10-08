import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import json
from .models import PromptComponent, Conversation, UserProfile, ChatSession, SportProfile, Sport 
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
from .tasks import get_ai_response, generate_title_and_summary
from datetime import datetime # <-- ADDED THIS IMPORT

logger = logging.getLogger(__name__)

# --- Vertex AI Initialization ---
load_dotenv()
# ------------------------------------

def landing_page(request):
    return render(request, 'recruiting/landing_page.html')

@login_required
def index(request, session_id=None):
    if session_id is None:
        latest_session = ChatSession.objects.filter(user=request.user).order_by('-updated_at').first()
        if latest_session:
            return redirect('view_session', session_id=latest_session.id)
    
    logger.info(f"User '{request.user.username}' loaded the agent page for session '{session_id}'.")
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
                CHAT_LIMIT = 3
                current_session_count = ChatSession.objects.filter(user=request.user).count()
                if current_session_count >= CHAT_LIMIT:
                    return JsonResponse({'error': 'Chat limit reached.'}, status=403)

                chat_session = ChatSession.objects.create(user=request.user, title=user_prompt[:100])
                session_id = chat_session.id
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Invalid session ID'}, status=404)

        player_context = ""
        try:
            profile = SportProfile.objects.select_related('sport').filter(user=request.user).first()
            if profile:
                player_context = (
                    f"CONTEXT: You are speaking to an athlete. "
                    f"Their profile is: Sport - {profile.sport.name}, "
                    f"Position - {profile.position}, "
                    f"Graduation Year - {profile.graduation_year}. "
                    f"Use this information to personalize your advice."
                )
        except SportProfile.DoesNotExist:
            logger.info(f"No SportProfile found for user '{request.user.username}'.")
            pass

        try:
            prompt_name = os.getenv('PROMPT_COMPONENT_NAME', 'recruiter_core_prompt')
            core_prompt_base = PromptComponent.objects.get(name=prompt_name).content
            
            # --- MODIFICATION STARTS HERE ---
            # 1. Get the current date and format it.
            current_date_str = datetime.now().strftime('%B %d, %Y')
            
            # 2. Create a new instruction that includes the current date.
            date_instruction = f"IMPORTANT: You must operate as if the current date is always {current_date_str}. Do not refer to this date as being in the future."
            
            # 3. Combine the instructions to create the final core prompt.
            core_prompt = f"{date_instruction}\n\n{player_context}\n\n{core_prompt_base}"
            # --- MODIFICATION ENDS HERE ---

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

    if result['status'] == 'SUCCESS':
        try:
            conv = Conversation.objects.filter(response_text=result['result']).latest('timestamp')
            session = conv.session
            # --- CORRECTED TRIGGER LOGIC ---
            # Trigger if it's the first message OR if the summary is currently empty.
            if session and (session.messages.count() == 1 or not session.summary):
                generate_title_and_summary.delay(str(session.id))
        except (Conversation.DoesNotExist, AttributeError):
            pass 
    
    return JsonResponse(result)

@login_required
def get_chat_sessions(request):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
    session_list = [
        {'id': str(session.id), 'title': session.title, 'summary': session.summary} 
        for session in sessions
    ]
    return JsonResponse({'sessions': session_list})

@login_required
def get_session_history(request, session_id):
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
        messages = session.messages.order_by('timestamp').values(
            'prompt_text', 'response_text', 'timestamp'
        )
        history = []
        for msg in messages:
            history.append({'type': 'user', 'text': msg['prompt_text'], 'timestamp': msg['timestamp']})
            history.append({'type': 'model', 'text': msg['response_text'], 'timestamp': msg['timestamp']})
        return JsonResponse({'history': history})
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found or access denied.'}, status=404)
    except Exception as e:
        logger.error(f"Error fetching session history for session {session_id}: {e}")
        return JsonResponse({'error': 'An internal error occurred.'}, status=500)

@login_required
def delete_session(request, session_id):
    if request.method == 'POST':
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            session.delete()
            return JsonResponse({'status': 'success', 'message': 'Session deleted.'})
        except ChatSession.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Session not found or access denied.'}, status=404)
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return JsonResponse({'status': 'error', 'message': 'An internal error occurred.'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

def register(request):
    # ... (code unchanged)
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
    # ... (code unchanged)
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