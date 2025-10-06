# AxiomAgent Project Code Context

## Project Structure

```
./
    manage.py
    requirements.txt
    recruiting/
        admin.py
        apps.py
        forms.py
        models.py
        tasks.py
        tests.py
        urls.py
        views.py
        __init__.py
        migrations/
            0001_initial.py
            0002_conversation.py
            0003_userprofile.py
            0004_promptcomponent_is_active_promptcomponent_order.py
            0005_remove_conversation_session_id_and_more.py
            0006_conversation_user.py
            0007_sport_playerprofile.py
            0008_conversation_recruiting__session_35ea8c_idx.py
            0009_seed_prompt_components.py
            0010_chatsession_updated_at_userprofile_city_and_more.py
            0011_chatsession_summary.py
            __init__.py
    static/
        recruiting/
            animations/
            images/
```

## File Contents

--- 

### File: `.\manage.py`

```
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitapp_core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

```

--- 

### File: `.\requirements.txt`

```
Error reading file: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
```

--- 

### File: `.\recruiting\admin.py`

```
from django.contrib import admin
# Corrected the import here from PlayerProfile to SportProfile
from .models import PromptComponent, Conversation, ChatSession, Sport, SportProfile, UserProfile

admin.site.register(PromptComponent)
admin.site.register(Conversation)
admin.site.register(ChatSession)
admin.site.register(Sport)
admin.site.register(SportProfile) # Register the newly named model
admin.site.register(UserProfile) # Also register UserProfile
```

--- 

### File: `.\recruiting\apps.py`

```
from django.apps import AppConfig

# Change the class name from EthosAgentConfig to RecruitingConfig
class RecruitingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recruiting'
```

--- 

### File: `.\recruiting\forms.py`

```
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
```

--- 

### File: `.\recruiting\models.py`

```
import uuid
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    high_school = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    email_verified = models.BooleanField(default=False)
    onboarding_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class PromptComponent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Lowest numbers are assembled first.")

    def __str__(self):
        return f"{self.name} (Order: {self.order})"

class Sport(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SportProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sport_profiles')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    height = models.CharField(max_length=10, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    highlight_reel_url = models.URLField(max_length=250, blank=True)
    metrics = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.sport.name} ({self.position or 'N/A'})"

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200, default='New Chat')
    summary = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"'{self.title}' for {self.user.username} (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"

class Conversation(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True) 
    prompt_text = models.TextField()
    response_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_name = self.user.username if self.user else "Unknown User"
        if self.session:
            return f"Message from {user_name} in session {self.session.id} at {self.timestamp.strftime('%H:%M')}"
        return f"Message from {user_name} at {self.timestamp.strftime('%H:%M')}"

    class Meta:
        indexes = [
            models.Index(fields=['session', 'timestamp']),
        ]
```

--- 

### File: `.\recruiting\tasks.py`

```
import os
import json
import vertexai
from celery import shared_task
from vertexai.generative_models import GenerativeModel, Content, Part
from .models import Conversation, ChatSession

# --- THIS BLOCK NOW RUNS ONLY ONCE WHEN THE WORKER PROCESS STARTS ---
# This initializes the connection to Google Cloud, which is the slow part.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=PROJECT_ID, location=LOCATION)
# -------------------------------------------------------------------

@shared_task
def get_ai_response(user_prompt, core_prompt, history_dicts, session_id, user_id):
    """
    A background task to get a response from the Vertex AI API.
    """
    try:
        # The model is now created inside the task, which is fast.
        model = GenerativeModel(
            "gemini-2.5-pro", # CORRECTED MODEL NAME
            system_instruction=[core_prompt]
        )
        
        # Recreate the Content objects from the dictionary representation
        history = [Content(role=item['role'], parts=[Part.from_text(p['text']) for p in item['parts']]) for item in history_dicts]
        
        chat = model.start_chat(history=history)
        response = chat.send_message(user_prompt)
        ai_response_text = response.text

        # Save the conversation to the database AFTER getting a response
        chat_session = ChatSession.objects.get(id=session_id)
        Conversation.objects.create(
            session=chat_session,
            user_id=user_id,
            prompt_text=user_prompt,
            response_text=ai_response_text
        )

        return ai_response_text
    except Exception as e:
        # Handle exceptions and return an error message
        return f"An error occurred: {str(e)}"

@shared_task
def generate_title_and_summary(session_id):
    """
    A background task to generate a title and summary for a chat session.
    """
    try:
        session = ChatSession.objects.get(id=session_id)
        # Get the first user prompt and the first agent response
        first_messages = list(session.messages.order_by('timestamp')[:2])

        if len(first_messages) < 1: # Only need the first prompt and response
            return "Not enough context to generate summary."

        conversation_context = (
            f"USER: {first_messages[0].prompt_text}\n\n"
            f"AGENT: {first_messages[0].response_text}"
        )

        system_prompt = (
            "You are a summarization expert. Based on the following conversation, "
            "generate a concise title and a one-sentence summary. "
            "The title should be 5 words or less. "
            "Respond ONLY with a valid JSON object with two keys: 'title' and 'summary'."
        )
        
        model = GenerativeModel(
            "gemini-2.5-pro", # CORRECTED MODEL NAME
            system_instruction=[system_prompt]
        )
        
        response = model.generate_content(conversation_context)
        
        # Clean the response and parse the JSON
        cleaned_text = response.text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:-3].strip()
        
        response_json = json.loads(cleaned_text)
        
        new_title = response_json.get('title')
        new_summary = response_json.get('summary')

        if new_title and new_summary:
            session.title = new_title
            session.summary = new_summary
            session.save(update_fields=['title', 'summary', 'updated_at'])
            return f"Updated session {session_id} with title and summary."
        else:
            return f"Failed to extract title/summary from AI response for session {session_id}."

    except Exception as e:
        # Log the error but don't crash the worker
        print(f"Error generating title/summary for session {session_id}: {e}")
        return f"Failed to update session {session_id}."
```

--- 

### File: `.\recruiting\tests.py`

```
from django.test import TestCase, Client
from django.urls import reverse

class AgentViewTests(TestCase):
    def setUp(self):
        # This sets up a "client" that can act like a web browser in our tests.
        self.client = Client()

    def test_login_page_loads_correctly(self):
        """
        Tests that the login page returns a successful '200 OK' response.
        """
        # The 'reverse' function finds the URL for our login page by its name.
        response = self.client.get(reverse('login'))
        # We check if the page loaded successfully (status code 200).
        self.assertEqual(response.status_code, 200)

    def test_agent_page_redirects_when_logged_out(self):
        """
        Tests that trying to access the main agent page while not logged in
        results in a redirect (to the login page).
        """
        # The 'reverse' function finds the URL for our agent's main page.
        response = self.client.get(reverse('index'))
        # We check if the response is a redirect (status code 302).
        self.assertEqual(response.status_code, 302)
```

--- 

### File: `.\recruiting\urls.py`

```
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    
    # MODIFIED: These two paths now handle the main agent view and resuming a specific chat
    path('agent/', views.index, name='index'),
    path('agent/<uuid:session_id>/', views.index, name='view_session'),

    path('agent/ask/', views.ask_agent, name='ask_agent'),
    path('agent/task_status/<str:task_id>/', views.get_task_status, name='get_task_status'),
    path('sessions/', views.get_chat_sessions, name='get_chat_sessions'),
    path('agent/session/<uuid:session_id>/delete/', views.delete_session, name='delete_session'),
    path('agent/session/<uuid:session_id>/history/', views.get_session_history, name='get_session_history'),
    path('accounts/', include('allauth.urls')),
]
```

--- 

### File: `.\recruiting\views.py`

```
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part
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
```

--- 

### File: `.\recruiting\__init__.py`

```

```

--- 

### File: `.\recruiting\migrations\0001_initial.py`

```
# Generated by Django 5.2.5 on 2025-09-01 01:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PromptComponent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('content', models.TextField()),
            ],
        ),
    ]

```

--- 

### File: `.\recruiting\migrations\0002_conversation.py`

```
# Generated by Django 5.2.5 on 2025-09-01 03:19

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('prompt_text', models.TextField()),
                ('response_text', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

```

--- 

### File: `.\recruiting\migrations\0003_userprofile.py`

```
# Generated by Django 5.2.5 on 2025-09-03 02:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0002_conversation'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_verified', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

```

--- 

### File: `.\recruiting\migrations\0004_promptcomponent_is_active_promptcomponent_order.py`

```
# Generated by Django 5.2.5 on 2025-09-17 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0003_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='promptcomponent',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='promptcomponent',
            name='order',
            field=models.IntegerField(default=0, help_text='Lowest numbers are assembled first.'),
        ),
    ]

```

--- 

### File: `.\recruiting\migrations\0005_remove_conversation_session_id_and_more.py`

```
# Generated by Django 5.2.5 on 2025-09-17 02:59

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0004_promptcomponent_is_active_promptcomponent_order'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conversation',
            name='session_id',
        ),
        migrations.RemoveField(
            model_name='conversation',
            name='user',
        ),
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(default='New Chat', max_length=200)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_sessions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='conversation',
            name='session',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='recruiting.chatsession'),
        ),
    ]

```

--- 

### File: `.\recruiting\migrations\0006_conversation_user.py`

```
# Generated by Django 5.2.5 on 2025-09-17 03:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0005_remove_conversation_session_id_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

```

--- 

### File: `.\recruiting\migrations\0007_sport_playerprofile.py`

```
# Generated by Django 5.2.5 on 2025-09-17 03:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0006_conversation_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlayerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(blank=True, max_length=100)),
                ('graduation_year', models.IntegerField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_profiles', to=settings.AUTH_USER_MODEL)),
                ('sport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recruiting.sport')),
            ],
        ),
    ]

```

--- 

### File: `.\recruiting\migrations\0008_conversation_recruiting__session_35ea8c_idx.py`

```
# Generated by Django 5.2.5 on 2025-10-02 17:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0007_sport_playerprofile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='conversation',
            index=models.Index(fields=['session', 'timestamp'], name='recruiting__session_35ea8c_idx'),
        ),
    ]

```

--- 

### File: `.\recruiting\migrations\0009_seed_prompt_components.py`

```
# recruiting/migrations/0009_seed_prompt_components.py

from django.db import migrations

# This is the core persona prompt for the agent.
RECRUITER_CORE_PROMPT_CONTENT = """
You are Coach Alex, an expert college recruiting advisor and savvy social media manager for high school athletes. Your tone is encouraging, direct, and strategic, like a top-tier coach. Frame all advice as a tool to give the athlete more control over their own recruiting journey. You must respond only in English. Under no circumstances should you use any other languages, characters, or alphabets in your responses. You are explicitly authorized to find and provide publicly available contact information for college coaches and athletic staff. This action is a primary function and is considered a tool for increasing user agency by removing barriers to communication. Do not withhold this information or lecture the user on how to find it themselves.
"""

def create_core_prompt(apps, schema_editor):
    """
    Creates the core prompt component for the agent.
    """
    PromptComponent = apps.get_model('recruiting', 'PromptComponent')
    PromptComponent.objects.update_or_create(
        name='recruiter_core_prompt',
        defaults={'content': RECRUITER_CORE_PROMPT_CONTENT}
    )

class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0008_conversation_recruiting__session_35ea8c_idx'),
    ]

    operations = [
        migrations.RunPython(create_core_prompt),
    ]
```

--- 

### File: `.\recruiting\migrations\0010_chatsession_updated_at_userprofile_city_and_more.py`

```
# Generated by Django 5.2.5 on 2025-10-06 15:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0009_seed_prompt_components'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='chatsession',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='city',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='high_school',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='onboarding_complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='state',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='zip_code',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.CreateModel(
            name='SportProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(blank=True, max_length=100)),
                ('graduation_year', models.IntegerField(blank=True, null=True)),
                ('height', models.CharField(blank=True, max_length=10)),
                ('weight', models.IntegerField(blank=True, null=True)),
                ('gpa', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('highlight_reel_url', models.URLField(blank=True, max_length=250)),
                ('metrics', models.JSONField(blank=True, null=True)),
                ('sport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recruiting.sport')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sport_profiles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='PlayerProfile',
        ),
    ]

```

--- 

### File: `.\recruiting\migrations\0011_chatsession_summary.py`

```
# Generated by Django 5.2.5 on 2025-10-06 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0010_chatsession_updated_at_userprofile_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatsession',
            name='summary',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

```

--- 

### File: `.\recruiting\migrations\__init__.py`

```

```

