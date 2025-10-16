# RecruitApp Project Code Context

## Project Structure

```
./
    manage.py
    requirements.txt
    recruitapp_core/
        __init__.py
        asgi.py
        celery.py
        settings.py
        urls.py
        wsgi.py
    recruiting/
        __init__.py
        admin.py
        apps.py
        forms.py
        models.py
        tasks.py
        tasks_enhanced.py
        tests.py
        urls.py
        views.py
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
            0012_ledgerentry_actionitem.py
            0013_enhanced_core_prompt.py
            __init__.py
        static/
            recruiting/
                css/
                    recruiting.css
        templates/
            recruiting/
                index.html
                landing_page.html
    templates/
        registration/
            login.html
            register.html
```

## File Contents

---

### File: `././manage.py`

```python
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

### File: `././requirements.txt`

```txt
cffi==2.0.0
gevent==25.9.1
greenlet==3.2.4
pycparser==2.23
setuptools==80.9.0
zope.event==6.0
zope.interface==8.0.1

```

---

### File: `././recruitapp_core/__init__.py`

```python
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)
```

---

### File: `././recruitapp_core/asgi.py`

```python
"""
ASGI config for recruitapp_core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitapp_core.settings')

application = get_asgi_application()

```

---

### File: `././recruitapp_core/celery.py`

```python
import os
import sys
from celery import Celery
from dotenv import load_dotenv

# Ensure the .env file is loaded for the standalone celery command
load_dotenv()

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitapp_core.settings')

app = Celery('recruitapp_core')

# Configure Celery directly using the environment variable.
# This is more robust than the 'config_from_object' method for this setup.
app.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
app.conf.result_backend = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.timezone = 'UTC'

# Windows-specific configuration: Use solo pool (works without gevent dependency issues)
# For production with concurrency, deploy to Linux or resolve gevent venv installation
if sys.platform == 'win32':
    app.conf.worker_pool = 'solo'  # Single-threaded, works reliably on Windows

    # To enable gevent (requires proper venv installation):
    # pip install --no-user gevent
    # Then uncomment:
    # app.conf.worker_pool = 'gevent'
    # app.conf.worker_concurrency = 10

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
```

---

### File: `././recruitapp_core/settings.py`

```python
# recruitapp_core/settings.py

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY')
DEVELOPMENT_MODE = os.environ.get('DEVELOPMENT_MODE') == 'True'
DEBUG = DEVELOPMENT_MODE

ALLOWED_HOSTS_STRING = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = ALLOWED_HOSTS_STRING.split(',')

INSTALLED_APPS = [
    'recruiting',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'whitenoise.runserver_nostatic',  <-- THIS LINE HAS BEEN REMOVED
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add WhiteNoise only in production
if not DEBUG:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'recruitapp_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'recruitapp_core.wsgi.application'

IS_BUILD_PROCESS = os.environ.get('IS_BUILD_PROCESS') == 'true'
if IS_BUILD_PROCESS:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
else:
    DATABASES = {'default': dj_database_url.config(conn_max_age=300, ssl_require=not DEVELOPMENT_MODE)}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'recruiting' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = '/agent/'
LOGOUT_REDIRECT_URL = '/'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1
SOCIALACCOUNT_PROVIDERS = {'google': {'SCOPE': ['profile', 'email'], 'AUTH_PARAMS': {'access_type': 'online'}}}

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

---

### File: `././recruitapp_core/urls.py`

```python
# recruitapp_core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),

    # This line correctly includes all URLs from your 'recruiting' app
    path('', include('recruiting.urls')),
]

# Serve static files in development using Django's staticfiles app
# This properly serves files from STATICFILES_DIRS during development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
```

---

### File: `././recruitapp_core/wsgi.py`

```python
"""
WSGI config for recruitapp_core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitapp_core.settings')

application = get_wsgi_application()

```

---

### File: `././recruiting/__init__.py`

```python

```

---

### File: `././recruiting/admin.py`

```python
from django.contrib import admin
# Corrected the import here from PlayerProfile to SportProfile
from .models import PromptComponent, Conversation, ChatSession, Sport, SportProfile, UserProfile, LedgerEntry, ActionItem

admin.site.register(PromptComponent)
admin.site.register(Conversation)
admin.site.register(ChatSession)
admin.site.register(Sport)
admin.site.register(SportProfile) # Register the newly named model
admin.site.register(UserProfile) # Also register UserProfile
admin.site.register(LedgerEntry) # Register new Ledger model
admin.site.register(ActionItem) # Register new Action Item model
```

---

### File: `././recruiting/apps.py`

```python
from django.apps import AppConfig

# Change the class name from EthosAgentConfig to RecruitingConfig
class RecruitingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recruiting'
```

---

### File: `././recruiting/forms.py`

```python
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
```

---

### File: `././recruiting/models.py`

```python
import uuid
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
# ... (UserProfile definition remains unchanged)
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
# ... (PromptComponent definition remains unchanged)
    name = models.CharField(max_length=100, unique=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Lowest numbers are assembled first.")

    def __str__(self):
        return f"{self.name} (Order: {self.order})"

class Sport(models.Model):
# ... (Sport definition remains unchanged)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SportProfile(models.Model):
# ... (SportProfile definition remains unchanged)
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
# ... (ChatSession definition remains unchanged)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200, default='New Chat')
    summary = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"'{self.title}' for {self.user.username} (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"

class Conversation(models.Model):
# ... (Conversation definition remains unchanged)
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

# --- START NEW MODELS FOR SPRINT 1 (Milestones 2 & 3) ---

class LedgerEntry(models.Model):
    """
    Represents a specific insight or piece of advice saved by the user
    from a conversation (Milestone 2: The "Ledger" Insights Hub).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ledger_entries')
    # Link back to the original message for context
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name='ledger_sources') 
    
    title = models.CharField(max_length=255, help_text="A short summary of the insight.")
    content = models.TextField(help_text="The full, saved insight/advice from the agent.")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ledger: {self.title} by {self.user.username}"

class ActionItem(models.Model):
    """
    Represents a structured, actionable task derived from the Ledger
    (Milestone 3: "Action Items" Roadmap).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_items')
    
    # Optional: Link to the LedgerEntry that inspired this action
    source_ledger_entry = models.ForeignKey(LedgerEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_actions')
    
    description = models.CharField(max_length=500)
    is_complete = models.BooleanField(default=False)
    priority = models.IntegerField(default=1) # 1: High, 2: Medium, 3: Low
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "COMPLETE" if self.is_complete else "PENDING"
        return f"[{status}] {self.description[:30]}..."

# --- END NEW MODELS ---
```

---

### File: `././recruiting/tasks.py`

```python
import os
import json
import vertexai
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from json.decoder import JSONDecodeError
import requests 

from vertexai.generative_models import (
    GenerativeModel, Part, Content, Tool, FunctionDeclaration,
    HarmBlockThreshold, HarmCategory,
    ToolConfig,
)

from .models import Conversation, ChatSession, ActionItem, LedgerEntry # <-- ADDED NEW MODELS

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=PROJECT_ID, location=LOCATION)

# --- Google Custom Search API Configuration ---
CUSTOM_SEARCH_ENGINE_ID = os.getenv("CUSTOM_SEARCH_ENGINE_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_API_URL = "https://www.googleapis.com/customsearch/v1"

# --- Tool Definitions (Unchanged) ---
search_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="google_search",
            description="This is a tool for searching the internet for up-to-date information.",
            parameters={
                "type": "object",
                "properties": { "query": { "type": "string", "description": "The query to search for"} },
                "required": ["query"]
            },
        )
    ]
)

TOOL_CONFIG_AUTO = ToolConfig(
    function_calling_config=ToolConfig.FunctionCallingConfig(
        mode=ToolConfig.FunctionCallingConfig.Mode.AUTO
    )
)

def google_search(query):
    # ... (google_search function remains unchanged)
    """
    Executes a search using the Google Custom Search API.
    Consolidates results into a single context string for the LLM.
    """
    print(f"Executing REAL Google Search for query: '{query}'")
    
    if not GOOGLE_API_KEY or not CUSTOM_SEARCH_ENGINE_ID:
        # Added a highly visible error message for debugging credential issues
        return {"error": "CRITICAL CREDENTIAL ERROR: Search API keys are missing or invalid."}
    
    params = {
        'key': GOOGLE_API_KEY,
        'cx': CUSTOM_SEARCH_ENGINE_ID,
        'q': query,
        'num': 5, # Request up to 5 results
    }

    try:
        response = requests.get(SEARCH_API_URL, params=params, timeout=5)
        
        # We assume the HTTP request succeeded, but if not, raise the status error
        response.raise_for_status() 
        search_data = response.json()
        
        context_string = "" 
        
        for i, item in enumerate(search_data.get('items', [])):
            context_string += (
                f"Result {i+1}:\n"
                f"Title: {item.get('title')}\n"
                f"Text: {item.get('snippet')}\n"
                f"Source URL: {item.get('link')}\n\n"
            )
        
        if not context_string:
            return {"search_results": "No relevant search results found."}

        return {"search_context": context_string}

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Google Search API: {e}")
        # Return a structured error for the LLM to synthesize
        return {"error": f"Search Service Unavailable. HTTP Request Failed: {e}"}
    except Exception as e:
        print(f"An unexpected error occurred during search processing: {e}")
        return {"error": "An internal error occurred during search."}


# --- AI Response Task (Unchanged) ---
@shared_task(bind=True)
def get_ai_response(self, user_prompt, core_prompt, history_dicts, session_id, user_id):
    # ... (get_ai_response remains unchanged)
    """
    Generates a response, handling tool execution manually, including multiple function calls.
    """
    try:
        model = GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=[core_prompt],
            tools=[search_tool]
        )

        history = [Content(role=item['role'], parts=[Part.from_text(p['text']) for p in item['parts']]) for item in history_dicts]
        
        messages_for_api = history + [Content(role="user", parts=[Part.from_text(user_prompt)])]

        # 1. First call to the model
        response = model.generate_content(
            messages_for_api,
            tool_config=TOOL_CONFIG_AUTO
        )

        function_calls = None
        if response.candidates and response.candidates[0].function_calls:
            function_calls = response.candidates[0].function_calls
            
        
        if function_calls:
            
            model_function_call_content = response.candidates[0].content
            
            messages_for_api.append(model_function_call_content)
            
            tool_responses = []

            # 2. Iterate through ALL function_call parts generated by the model
            for part in model_function_call_content.parts:
                if part.function_call:
                    function_call = part.function_call
                    function_name = function_call.name
                    
                    if function_name == "google_search":
                        args = dict(function_call.args)
                        
                        tool_output = google_search(**args)
                        
                        tool_responses.append(
                            Part.from_function_response(
                                name=function_name,
                                response=tool_output
                            )
                        )

            # 3. Append ALL tool responses to the history
            if tool_responses:
                messages_for_api.append(
                    Content(role="tool", parts=tool_responses)
                )

                # 4. Second call to the model to synthesize the final text response
                response = model.generate_content(messages_for_api, tool_config=TOOL_CONFIG_AUTO)
            
        
        # --- FIX: Defensive text extraction to prevent SDK ValueError from crashing task ---
        try:
            ai_response_text = response.text
        except ValueError:
            # Fallback to direct extraction of text from the first candidate part
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                text_part = next((p.text for p in response.candidates[0].content.parts if p.text), None)
                if text_part:
                    ai_response_text = text_part
                else:
                    # If all else fails, use a generic error message
                    ai_response_text = "I encountered an internal error while synthesizing my response, but the search was successful. Please try asking again."
            else:
                ai_response_text = "I encountered an unrecoverable internal error."


        chat_session = ChatSession.objects.get(id=session_id)
        Conversation.objects.create(
            session=chat_session,
            user_id=user_id,
            prompt_text=user_prompt,
            response_text=ai_response_text
        )
        return ai_response_text

    except ObjectDoesNotExist:
        return "Chat session not found."
    except Exception as e:
        print(f"An unexpected error occurred in AI agent task: {e}. Retrying in 60s.")
        raise self.retry(exc=e, countdown=60)


# --- NEW TASK FOR MILESTONE 3: GENERATING ACTION ITEMS ---

@shared_task(bind=True)
def generate_action_items_task(self, user_id, ledger_entry_id, ledger_content):
    """
    Analyzes the content of a LedgerEntry and generates structured ActionItem records.
    """
    try:
        system_prompt = (
            "You are an expert project manager and recruiting strategist. Your task is to analyze "
            "the provided advice/insight and distill it into 3 to 5 clear, concrete, and actionable "
            "steps (Action Items) for a student-athlete. Each action item must be a short, direct "
            "sentence (max 15 words). Ignore any background context or titles, focus strictly on the action."
            "Respond ONLY with a single JSON array containing objects with the key 'description'. "
            "DO NOT include any markdown fences (```json) or introductory text. "
            "Example response: [{'description': 'Research 10 target schools this week.'}, {'description': 'Create a new highlight reel clip.'}]"
        )
        
        model = GenerativeModel("gemini-2.5-flash", system_instruction=[system_prompt])
        
        # The content sent to the model is just the advice from the Ledger
        response = model.generate_content(ledger_content)
        
        raw_text = response.text.strip()
        cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()

        try:
            # Parse the structured list of action items
            action_list = json.loads(cleaned_text)
            
            if not isinstance(action_list, list):
                raise JSONDecodeError("Root is not a list.", cleaned_text, 0)
            
            # Retrieve the necessary objects
            user = User.objects.get(pk=user_id)
            source_entry = LedgerEntry.objects.get(pk=ledger_entry_id)

            created_count = 0
            for action_data in action_list:
                description = action_data.get('description')
                if description:
                    ActionItem.objects.create(
                        user=user,
                        source_ledger_entry=source_entry,
                        description=description,
                        priority=2 # Default to Medium priority for generated tasks
                    )
                    created_count += 1
            
            return f"Successfully created {created_count} Action Items from Ledger Entry {ledger_entry_id}."

        except JSONDecodeError as jde:
            print(f"JSON Decoding Error: {jde}. Raw Response: {raw_text}")
            return f"Failed to generate Action Items: Bad JSON format."
        
    except (ObjectDoesNotExist, Exception) as e:
        print(f"Error generating action items: {e}")
        raise self.retry(exc=e, countdown=60)


# --- Title and Summary Task (Unchanged) ---
@shared_task(bind=True)
def generate_title_and_summary(self, session_id):
    # ... (generate_title_and_summary remains unchanged)
    try:
        session = ChatSession.objects.get(id=session_id)
        messages = session.messages.order_by('timestamp')[:4] 
        if not messages or len(messages) < 2:
            return "Not enough context for summary."
            
        context_parts = []
        for msg in messages:
            context_parts.append(f"USER: {msg.prompt_text}")
            if msg.response_text:
                context_parts.append(f"AGENT: {msg.response_text}")
                
        conversation_context = "\n\n".join(context_parts)
        
        system_prompt = (
            "You are a summarization expert. Analyze the provided conversation snippet. "
            "Generate a concise, engaging title (max 5 words) and a brief summary (max 20 words). "
            "Respond ONLY with a single valid JSON object containing the keys 'title' and 'summary'. "
            "DO NOT include any markdown fences (```json) or introductory text."
        )
        
        model = GenerativeModel("gemini-2.5-flash", system_instruction=[system_prompt])
        response = model.generate_content(conversation_context)
        
        raw_text = response.text.strip()
        
        cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
        
        try:
            response_json = json.loads(cleaned_text)
            new_title = response_json.get('title')
            new_summary = response_json.get('summary')
            
            if new_title and new_summary:
                session.title = new_title
                session.summary = new_summary
                session.save(update_fields=['title', 'summary'])
                return f"Updated session {session_id}."
            else:
                print(f"Failed to extract title/summary for session {session_id}. Keys missing in valid JSON: {response_json}")
                return f"Failed to extract title/summary for session {session_id}."

        except JSONDecodeError as jde:
            print(f"JSON Decoding Error for session {session_id}: {jde}")
            print(f"Raw Model Response: {raw_text}")
            return f"Failed to extract title/summary for session {session_id} due to bad JSON formatting."
            
    except ChatSession.DoesNotExist:
        return f"Chat session {session_id} not found."
    except Exception as e:
        print(f"Error generating title/summary for session {session_id}: {e}")
        raise self.retry(exc=e, countdown=60)
```

---

### File: `././recruiting/tasks_enhanced.py`

```python
import os
import json
import vertexai
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from json.decoder import JSONDecodeError
import requests
from datetime import datetime

from vertexai.generative_models import (
    GenerativeModel, Part, Content, Tool, FunctionDeclaration,
    HarmBlockThreshold, HarmCategory,
    ToolConfig,
)

from .models import Conversation, ChatSession, ActionItem, LedgerEntry

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=PROJECT_ID, location=LOCATION)

# --- Google Custom Search API Configuration ---
CUSTOM_SEARCH_ENGINE_ID = os.getenv("CUSTOM_SEARCH_ENGINE_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_API_URL = "https://www.googleapis.com/customsearch/v1"

# ============================================================================
# ENHANCED SEARCH TOOL WITH DETAILED DESCRIPTION
# ============================================================================

search_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="google_search",
            description=(
                "Searches the internet for current, factual information about college athletics recruiting, "
                "coach contact information, program statistics, recruiting rules, deadlines, and recent news. "

                "**WHEN TO USE THIS TOOL:**\n"
                "- User asks about specific colleges, coaches, or athletic programs\n"
                "- User needs current recruiting deadlines, rules, or regulations (NCAA/NAIA)\n"
                "- User asks 'what are the best schools for [sport/position]'\n"
                "- User needs coach contact information (emails, phone numbers)\n"
                "- User asks about recent program achievements, rankings, or news\n"
                "- Any question requiring facts from after your knowledge cutoff\n"
                "- When you're uncertain about specific data (don't guess!)\n\n"

                "**SEARCH QUERY BEST PRACTICES:**\n"
                "- Be specific: Instead of 'football recruiting', use 'Division 1 football recruiting rules 2025'\n"
                "- Include relevant context: '[Sport] [Division] [College Name] coach contact'\n"
                "- Use official terminology: 'NCAA Division 1', 'NAIA', 'commitment period'\n"
                "- For coach info: '[College] [Sport] coaching staff email' or '[Coach Name] [College] contact'\n"
                "- For rankings: '[Sport] college rankings 2025' or '[Conference] standings 2024'\n\n"

                "**MULTIPLE SEARCHES:**\n"
                "You can call this tool multiple times in one turn if needed. For complex questions, "
                "break them into focused searches (e.g., one for rules, one for coach contacts).\n\n"

                "**IMPORTANT:** Always search when you need current information. Don't rely on potentially "
                "outdated knowledge. The user is counting on accurate, up-to-date advice."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The specific, detailed search query. Be precise and include all relevant context "
                            "(sport, division, year, college name, etc.). Examples: 'Stanford football coach email 2025', "
                            "'NCAA Division 1 volleyball recruiting dead period 2025', 'Top lacrosse programs Northeast 2024'"
                        )
                    }
                },
                "required": ["query"]
            },
        )
    ]
)

TOOL_CONFIG_AUTO = ToolConfig(
    function_calling_config=ToolConfig.FunctionCallingConfig(
        mode=ToolConfig.FunctionCallingConfig.Mode.AUTO
    )
)

# ============================================================================
# ENHANCED SEARCH FUNCTION WITH VALIDATION & CITATION
# ============================================================================

def google_search(query):
    """
    Executes a search using the Google Custom Search API with enhanced result processing.

    Improvements:
    - Increased result count to 8 for better coverage
    - Adds metadata for source validation
    - Includes search timestamp
    - Better error messaging
    """
    print(f"[SEARCH] Executing query: '{query}'")

    if not GOOGLE_API_KEY or not CUSTOM_SEARCH_ENGINE_ID:
        return {
            "error": "CRITICAL: Search API credentials are missing. Unable to retrieve current information.",
            "fallback_instruction": "Inform the user that you cannot access live search results right now, but offer to provide general guidance based on your training data with a clear disclaimer about currency."
        }

    params = {
        'key': GOOGLE_API_KEY,
        'cx': CUSTOM_SEARCH_ENGINE_ID,
        'q': query,
        'num': 8,  # Increased from 5 to 8 for better coverage
    }

    try:
        response = requests.get(SEARCH_API_URL, params=params, timeout=10)  # Increased timeout
        response.raise_for_status()
        search_data = response.json()

        # Enhanced result processing
        results = []
        for i, item in enumerate(search_data.get('items', []), 1):
            result_entry = {
                'rank': i,
                'title': item.get('title', 'No title'),
                'snippet': item.get('snippet', 'No description available'),
                'url': item.get('link', 'No URL'),
                'source_domain': item.get('displayLink', 'Unknown source')
            }
            results.append(result_entry)

        if not results:
            return {
                "status": "no_results",
                "message": f"No search results found for query: '{query}'",
                "suggestion": "Try rephrasing your search with different keywords or check for typos."
            }

        # Format results for LLM consumption
        context_string = f"Search Query: '{query}'\n"
        context_string += f"Search Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n"
        context_string += f"Total Results: {len(results)}\n\n"

        for result in results:
            context_string += f"[{result['rank']}] {result['title']}\n"
            context_string += f"    Source: {result['source_domain']}\n"
            context_string += f"    {result['snippet']}\n"
            context_string += f"    URL: {result['url']}\n\n"

        return {
            "status": "success",
            "query": query,
            "result_count": len(results),
            "search_context": context_string,
            "sources": [r['url'] for r in results]  # Separate list for citation tracking
        }

    except requests.exceptions.Timeout:
        return {
            "error": "Search request timed out. Internet connection may be slow.",
            "suggestion": "Provide an answer based on your training data with a disclaimer."
        }
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Search API request failed: {e}")
        return {
            "error": f"Search service temporarily unavailable: {str(e)}",
            "suggestion": "Apologize to the user and offer general guidance with a clear disclaimer."
        }
    except Exception as e:
        print(f"[ERROR] Unexpected error during search: {e}")
        return {
            "error": "An internal error occurred during search processing.",
            "suggestion": "Inform the user and provide fallback guidance."
        }


# ============================================================================
# ENHANCED AI RESPONSE TASK WITH IMPROVED SEARCH HANDLING
# ============================================================================

@shared_task(bind=True)
def get_ai_response(self, user_prompt, core_prompt, history_dicts, session_id, user_id):
    """
    Generates a response with enhanced search tool usage and source citation.

    Improvements:
    - Better search result handling
    - Source citation in responses
    - Search quality validation
    - Improved error recovery
    """
    try:
        model = GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=[core_prompt],
            tools=[search_tool]
        )

        history = [
            Content(
                role=item['role'],
                parts=[Part.from_text(p['text']) for p in item['parts']]
            )
            for item in history_dicts
        ]

        messages_for_api = history + [Content(role="user", parts=[Part.from_text(user_prompt)])]

        # First model call
        response = model.generate_content(
            messages_for_api,
            tool_config=TOOL_CONFIG_AUTO
        )

        # Check for function calls
        function_calls = None
        if response.candidates and response.candidates[0].function_calls:
            function_calls = response.candidates[0].function_calls

        # Track sources for citation
        cited_sources = []

        if function_calls:
            model_function_call_content = response.candidates[0].content
            messages_for_api.append(model_function_call_content)

            tool_responses = []

            # Execute all function calls
            for part in model_function_call_content.parts:
                if part.function_call:
                    function_call = part.function_call
                    function_name = function_call.name

                    if function_name == "google_search":
                        args = dict(function_call.args)
                        print(f"[AGENT] Executing search: {args.get('query', 'No query')}")

                        tool_output = google_search(**args)

                        # Track sources if search was successful
                        if tool_output.get('status') == 'success':
                            cited_sources.extend(tool_output.get('sources', []))

                        tool_responses.append(
                            Part.from_function_response(
                                name=function_name,
                                response=tool_output
                            )
                        )

            # Append all tool responses
            if tool_responses:
                messages_for_api.append(
                    Content(role="tool", parts=tool_responses)
                )

                # Second model call to synthesize response
                response = model.generate_content(
                    messages_for_api,
                    tool_config=TOOL_CONFIG_AUTO
                )

        # Extract response text with defensive handling
        try:
            ai_response_text = response.text
        except ValueError:
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                text_part = next((p.text for p in response.candidates[0].content.parts if p.text), None)
                if text_part:
                    ai_response_text = text_part
                else:
                    ai_response_text = "I encountered an internal error while processing the search results. Please try rephrasing your question."
            else:
                ai_response_text = "I encountered an unexpected error. Please try again."

        # Add source citation if searches were performed
        if cited_sources:
            unique_sources = list(dict.fromkeys(cited_sources[:5]))  # Limit to top 5 unique sources
            ai_response_text += "\n\n---\n**Sources:**\n"
            for i, source in enumerate(unique_sources, 1):
                ai_response_text += f"{i}. {source}\n"

        # Save conversation
        chat_session = ChatSession.objects.get(id=session_id)
        Conversation.objects.create(
            session=chat_session,
            user_id=user_id,
            prompt_text=user_prompt,
            response_text=ai_response_text
        )

        print(f"[AGENT] Response generated. Searches performed: {len(cited_sources) > 0}")
        return ai_response_text

    except ObjectDoesNotExist:
        return "Chat session not found."
    except Exception as e:
        print(f"[ERROR] AI agent task failed: {e}")
        raise self.retry(exc=e, countdown=60)


# ============================================================================
# ENHANCED ACTION ITEM GENERATION (Unchanged but included for completeness)
# ============================================================================

@shared_task(bind=True)
def generate_action_items_task(self, user_id, ledger_entry_id, ledger_content):
    """
    Analyzes the content of a LedgerEntry and generates structured ActionItem records.
    """
    try:
        from django.contrib.auth.models import User

        system_prompt = (
            "You are an expert project manager and recruiting strategist. Your task is to analyze "
            "the provided advice/insight and distill it into 3 to 5 clear, concrete, and actionable "
            "steps (Action Items) for a student-athlete. Each action item must be a short, direct "
            "sentence (max 15 words). Ignore any background context or titles, focus strictly on the action."
            "Respond ONLY with a single JSON array containing objects with the key 'description'. "
            "DO NOT include any markdown fences (```json) or introductory text. "
            "Example response: [{'description': 'Research 10 target schools this week.'}, {'description': 'Create a new highlight reel clip.'}]"
        )

        model = GenerativeModel("gemini-2.5-flash", system_instruction=[system_prompt])
        response = model.generate_content(ledger_content)

        raw_text = response.text.strip()
        cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()

        try:
            action_list = json.loads(cleaned_text)

            if not isinstance(action_list, list):
                raise JSONDecodeError("Root is not a list.", cleaned_text, 0)

            user = User.objects.get(pk=user_id)
            source_entry = LedgerEntry.objects.get(pk=ledger_entry_id)

            created_count = 0
            for action_data in action_list:
                description = action_data.get('description')
                if description:
                    ActionItem.objects.create(
                        user=user,
                        source_ledger_entry=source_entry,
                        description=description,
                        priority=2
                    )
                    created_count += 1

            return f"Successfully created {created_count} Action Items from Ledger Entry {ledger_entry_id}."

        except JSONDecodeError as jde:
            print(f"[ERROR] JSON parsing failed: {jde}. Raw: {raw_text}")
            return "Failed to generate Action Items: Bad JSON format."

    except (ObjectDoesNotExist, Exception) as e:
        print(f"[ERROR] Action item generation failed: {e}")
        raise self.retry(exc=e, countdown=60)


# ============================================================================
# ENHANCED TITLE/SUMMARY GENERATION (Unchanged but included for completeness)
# ============================================================================

@shared_task(bind=True)
def generate_title_and_summary(self, session_id):
    try:
        session = ChatSession.objects.get(id=session_id)
        messages = session.messages.order_by('timestamp')[:4]

        if not messages or len(messages) < 2:
            return "Not enough context for summary."

        context_parts = []
        for msg in messages:
            context_parts.append(f"USER: {msg.prompt_text}")
            if msg.response_text:
                context_parts.append(f"AGENT: {msg.response_text}")

        conversation_context = "\n\n".join(context_parts)

        system_prompt = (
            "You are a summarization expert. Analyze the provided conversation snippet. "
            "Generate a concise, engaging title (max 5 words) and a brief summary (max 20 words). "
            "Respond ONLY with a single valid JSON object containing the keys 'title' and 'summary'. "
            "DO NOT include any markdown fences (```json) or introductory text."
        )

        model = GenerativeModel("gemini-2.5-flash", system_instruction=[system_prompt])
        response = model.generate_content(conversation_context)

        raw_text = response.text.strip()
        cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()

        try:
            response_json = json.loads(cleaned_text)
            new_title = response_json.get('title')
            new_summary = response_json.get('summary')

            if new_title and new_summary:
                session.title = new_title
                session.summary = new_summary
                session.save(update_fields=['title', 'summary'])
                return f"Updated session {session_id}."
            else:
                print(f"[ERROR] Missing keys in JSON for session {session_id}")
                return f"Failed to extract title/summary for session {session_id}."

        except JSONDecodeError as jde:
            print(f"[ERROR] JSON parsing failed for session {session_id}: {jde}")
            return f"Failed to extract title/summary for session {session_id}."

    except ChatSession.DoesNotExist:
        return f"Chat session {session_id} not found."
    except Exception as e:
        print(f"[ERROR] Title/summary generation failed: {e}")
        raise self.retry(exc=e, countdown=60)

```

---

### File: `././recruiting/tests.py`

```python
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

### File: `././recruiting/urls.py`

```python
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
    
    # --- START NEW URLS FOR SPRINT 1 ---
    
    # Ledger Routes (Milestone 2)
    path('ledger/', views.ledger_list, name='ledger_list'),
    path('ledger/save/', views.save_to_ledger, name='save_to_ledger'),
    path('ledger/<int:entry_id>/delete/', views.delete_ledger_entry, name='delete_ledger_entry'),
    
    # Action Item Routes (Milestone 3)
    path('action-items/', views.action_items_list, name='action_items_list'),
    path('action-items/generate/', views.generate_action_items, name='generate_action_items'),
    path('action-items/<int:item_id>/toggle/', views.toggle_action_item_complete, name='toggle_action_item_complete'),

    # --- END NEW URLS ---
    
    path('accounts/', include('allauth.urls')),
]
```

---

### File: `././recruiting/views.py`

```python
import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
import json
from .models import PromptComponent, Conversation, UserProfile, ChatSession, SportProfile, Sport, LedgerEntry, ActionItem 
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
from .tasks import get_ai_response, generate_title_and_summary, generate_action_items_task # <-- IMPORT NEW TASK
from datetime import datetime

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
# ... (ask_agent view remains unchanged)
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
# ... (get_task_status view remains unchanged)
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

# ... (get_chat_sessions, get_session_history, delete_session views remain unchanged)
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
        # MODIFIED: Include 'id' in the values() call
        messages = session.messages.order_by('timestamp').values(
            'id', 'prompt_text', 'response_text', 'timestamp'
        )
        history = []
        for msg in messages:
            # User message has no ID reference needed by the Ledger
            history.append({'type': 'user', 'text': msg['prompt_text'], 'timestamp': msg['timestamp'], 'id': None}) 
            
            # Agent message requires the Conversation ID ('id' field) for Ledger functionality
            history.append({'type': 'model', 'text': msg['response_text'], 'timestamp': msg['timestamp'], 'id': str(msg['id'])}) 
        
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


# ------------------------------------
# --- NEW VIEWS FOR LEDGER (Milestone 2) ---
# ------------------------------------

@login_required
def ledger_list(request):
    """API endpoint to get a list of all Ledger entries for the user."""
    entries = LedgerEntry.objects.filter(user=request.user).order_by('-created_at').values(
        'id', 'title', 'content', 'created_at', 'conversation_id'
    )
    # Return as JSON for front-end rendering
    return JsonResponse({'ledger_entries': list(entries)})

@login_required
def save_to_ledger(request):
    """API endpoint to save a piece of advice to the Ledger."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # The client must send the ID of the specific Conversation message
            conversation_id = data.get('conversation_id')
            title = data.get('title') # User-provided title for elegance
            content = data.get('content') # Agent's response text

            if not title or not content:
                return JsonResponse({'status': 'error', 'message': 'Title and content are required.'}, status=400)
            
            conversation = None
            if conversation_id:
                # Ensure the conversation belongs to the user
                conversation = get_object_or_404(Conversation, pk=conversation_id, user_id=request.user.id)

            LedgerEntry.objects.create(
                user=request.user,
                conversation=conversation,
                title=title,
                content=content
            )
            
            return JsonResponse({'status': 'success', 'message': 'Insight successfully saved to Ledger.'})
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            logger.error(f"Error saving to ledger: {e}")
            return JsonResponse({'status': 'error', 'message': 'An internal error occurred.'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed.'}, status=405)

@login_required
def delete_ledger_entry(request, entry_id):
    """API endpoint to delete a Ledger entry."""
    entry = get_object_or_404(LedgerEntry, pk=entry_id, user=request.user)
    if request.method == 'POST':
        entry.delete()
        return JsonResponse({'status': 'success', 'message': 'Ledger entry deleted.'})
    return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed.'}, status=405)


# ------------------------------------
# --- NEW VIEWS FOR ACTION ITEMS (Milestone 3) ---
# ------------------------------------

@login_required
def action_items_list(request):
    """API endpoint to get the list of active and completed Action Items."""
    items = ActionItem.objects.filter(user=request.user).order_by('-created_at').values(
        'id', 'description', 'is_complete', 'priority', 'due_date', 'created_at', 'source_ledger_entry_id'
    )
    # Split into active and completed for front-end categorization
    active_items = [item for item in items if not item['is_complete']]
    completed_items = [item for item in items if item['is_complete']]
    
    return JsonResponse({
        'active_items': active_items,
        'completed_items': completed_items
    })


@login_required
def generate_action_items(request):
    """
    API endpoint to trigger the AI analysis of a specific Ledger entry to generate Action Items.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ledger_entry_id = data.get('ledger_entry_id')
            
            if not ledger_entry_id:
                return JsonResponse({'status': 'error', 'message': 'ledger_entry_id is required.'}, status=400)

            # Retrieve the specific Ledger Entry
            ledger_entry = get_object_or_404(LedgerEntry, pk=ledger_entry_id, user=request.user)

            # Trigger the Celery task
            task = generate_action_items_task.delay(
                request.user.id, 
                ledger_entry.id,
                ledger_entry.content
            )
            
            return JsonResponse({'status': 'success', 'message': 'Action Item generation task started.', 'task_id': task.id})
        
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            logger.error(f"Error triggering action item generation: {e}")
            return JsonResponse({'status': 'error', 'message': f'An internal error occurred: {e}'}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed.'}, status=405)

@login_required
def toggle_action_item_complete(request, item_id):
# ... (toggle_action_item_complete view remains unchanged)
    item = get_object_or_404(ActionItem, pk=item_id, user=request.user)
    if request.method == 'POST':
        item.is_complete = not item.is_complete
        item.save(update_fields=['is_complete'])
        return JsonResponse({'status': 'success', 'is_complete': item.is_complete, 'message': 'Action item status updated.'})
    return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed.'}, status=405)

# ... (register and verify_email remain unchanged)
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
```

---

### File: `././recruiting/migrations/0001_initial.py`

```python
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

### File: `././recruiting/migrations/0002_conversation.py`

```python
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

### File: `././recruiting/migrations/0003_userprofile.py`

```python
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

### File: `././recruiting/migrations/0004_promptcomponent_is_active_promptcomponent_order.py`

```python
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

### File: `././recruiting/migrations/0005_remove_conversation_session_id_and_more.py`

```python
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

### File: `././recruiting/migrations/0006_conversation_user.py`

```python
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

### File: `././recruiting/migrations/0007_sport_playerprofile.py`

```python
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

### File: `././recruiting/migrations/0008_conversation_recruiting__session_35ea8c_idx.py`

```python
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

### File: `././recruiting/migrations/0009_seed_prompt_components.py`

```python
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

### File: `././recruiting/migrations/0010_chatsession_updated_at_userprofile_city_and_more.py`

```python
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

### File: `././recruiting/migrations/0011_chatsession_summary.py`

```python
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

### File: `././recruiting/migrations/0012_ledgerentry_actionitem.py`

```python
# Generated by Django 5.2.5 on 2025-10-10 10:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0011_chatsession_summary'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LedgerEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='A short summary of the insight.', max_length=255)),
                ('content', models.TextField(help_text='The full, saved insight/advice from the agent.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ledger_sources', to='recruiting.conversation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ledger_entries', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ActionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=500)),
                ('is_complete', models.BooleanField(default=False)),
                ('priority', models.IntegerField(default=1)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('source_ledger_entry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='generated_actions', to='recruiting.ledgerentry')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_items', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
```

---

### File: `././recruiting/migrations/0013_enhanced_core_prompt.py`

```python
# recruiting/migrations/0013_enhanced_core_prompt.py

from django.db import migrations

# ============================================================================
# ENHANCED CORE PROMPT WITH SEARCH STRATEGY GUIDANCE
# ============================================================================

RECRUITER_CORE_PROMPT_ENHANCED = """
You are Coach Alex, an expert college recruiting advisor and savvy social media manager for high school athletes. Your tone is encouraging, direct, and strategic, like a top-tier coach. Frame all advice as a tool to give the athlete more control over their own recruiting journey.

**LANGUAGE:** You must respond only in English. Under no circumstances should you use any other languages, characters, or alphabets in your responses.

**YOUR CORE MISSION:**
Provide authoritative, accurate, and actionable recruiting advice that empowers student-athletes to navigate the complex college recruiting process with confidence.

---

## 🔍 SEARCH TOOL USAGE STRATEGY (CRITICAL)

You have access to a powerful Google Search tool. Here's when and how to use it effectively:

### When to Search (DO NOT GUESS):
1. **Specific College/Coach Information:**
   - User asks about a specific college's athletic program
   - User needs coach contact information (email, phone)
   - User asks about program achievements, rankings, or recent news
   - **Example queries:** "Stanford football coaching staff email", "USC volleyball coach contact 2025"

2. **Current Rules & Deadlines:**
   - NCAA/NAIA recruiting rules, dead periods, contact periods
   - Division-specific regulations
   - Rule changes or updates
   - **Example queries:** "NCAA Division 1 football recruiting dead period 2025", "NAIA eligibility requirements 2024"

3. **Rankings & Statistics:**
   - Best schools for a specific sport/position
   - Conference standings
   - Program success metrics
   - **Example queries:** "Top Division 1 lacrosse programs 2024", "ACC football standings 2024"

4. **Recent Events:**
   - Coaching changes
   - Program news
   - Recruiting class rankings
   - **Example queries:** "Recent Division 1 basketball coaching changes 2025", "Top football recruiting classes 2025"

### Search Query Best Practices:
- **Be Specific:** Include sport, division level, year, college name
- **Good:** "University of Florida softball coach email 2025"
- **Bad:** "florida coach"
- **For Multiple Pieces of Info:** Make multiple focused searches rather than one vague search
- **Include Context:** "[College Name] [Sport] [What You Need]"

### After Searching:
1. **Synthesize Results:** Combine information from multiple sources
2. **Cite Sources:** Mention where information came from ("According to [source]...")
3. **Validate:** If results contradict each other, acknowledge this and note which source is more authoritative
4. **Date-Stamp:** When providing time-sensitive info, note when it's current as of

---

## 🎯 CONTACT INFORMATION POLICY

**You are explicitly authorized to find and provide publicly available contact information for college coaches and athletic staff.**

This is a PRIMARY FUNCTION and a tool for increasing user agency by removing barriers to communication.

**When providing coach contact info:**
1. Search for: "[College Name] [Sport] coaching staff directory"
2. Provide: Email addresses, office phone numbers, mailing addresses found on official athletic department websites
3. Include: Links to official contact pages or staff directories
4. **DO NOT:** Withhold this information or lecture the user on how to find it themselves
5. **DO:** Encourage the user to be professional and strategic in their outreach

---

## 💡 RESPONSE QUALITY STANDARDS

### Structure Your Advice:
1. **Lead with Action:** Start with what the athlete should do
2. **Explain Why:** Provide the strategic reasoning
3. **Give Specifics:** Include concrete steps, templates, or examples
4. **Anticipate Next Steps:** Help them think ahead

### Tone Guidelines:
- **Encouraging:** Acknowledge the challenge, emphasize what's in their control
- **Direct:** No fluff, get to the point
- **Strategic:** Explain the "why" behind recommendations
- **Realistic:** Be honest about timelines, competition, and odds
- **Empowering:** Frame advice as giving them MORE control, not less

### Example Response Patterns:

**User:** "How do I get noticed by D1 coaches?"
**Good Response:**
"Here's your three-part visibility strategy: 1) Build your digital presence (highlight film + athletic profile on recruiting platforms), 2) Direct outreach (email campaigns to 20-30 target coaches), and 3) Attend the right showcases. Let's start with #2 since that's entirely in your control. I'll search for specific coaches you should target. What position do you play and what region are you targeting?"

**Bad Response:**
"You should probably make a highlight film and go to camps."

---

## 🚫 WHAT NOT TO DO

1. **Don't Guess:** If you don't know current information, search for it
2. **Don't Be Vague:** "Research schools" is not actionable; "Email 10 coaches this week using this template" is
3. **Don't Overwhelm:** Break complex processes into sequential steps
4. **Don't Deflate:** Even if odds are long, focus on what's controllable
5. **Don't Ignore Context:** Always consider the user's sport, position, graduation year, and goals

---

## 📊 INFORMATION HIERARCHY (Trust Levels)

When synthesizing information, prioritize sources in this order:
1. **Official NCAA/NAIA websites** (rules, eligibility)
2. **Official college athletic department websites** (coach contacts, program info)
3. **Verified sports news outlets** (ESPN, Athletic, conference websites)
4. **Recruiting platforms** (247Sports, Rivals, etc.)
5. **General sources** (validate against above)

If sources conflict, note the discrepancy and explain which is more authoritative.

---

## 🎓 YOUR EXPERTISE AREAS

You have deep knowledge in:
- NCAA Division 1, 2, 3 recruiting processes
- NAIA and Junior College recruiting
- Timeline and rule compliance
- Email outreach strategies
- Social media best practices for athletes
- Highlight film creation
- Showcases and camp strategy
- Academic eligibility (NCAA Eligibility Center)
- Financial aid and scholarship negotiation
- Transfer portal navigation

---

**Remember:** Your goal is to make the athlete feel MORE in control, MORE informed, and MORE confident. Every response should move them forward with specific, actionable next steps.
"""

def update_core_prompt(apps, schema_editor):
    """
    Updates the core prompt to the enhanced version with search strategy guidance.
    """
    PromptComponent = apps.get_model('recruiting', 'PromptComponent')
    PromptComponent.objects.update_or_create(
        name='recruiter_core_prompt',
        defaults={'content': RECRUITER_CORE_PROMPT_ENHANCED}
    )

def revert_core_prompt(apps, schema_editor):
    """
    Reverts to the original simpler prompt if needed.
    """
    PromptComponent = apps.get_model('recruiting', 'PromptComponent')
    ORIGINAL_PROMPT = """
You are Coach Alex, an expert college recruiting advisor and savvy social media manager for high school athletes. Your tone is encouraging, direct, and strategic, like a top-tier coach. Frame all advice as a tool to give the athlete more control over their own recruiting journey. You must respond only in English. Under no circumstances should you use any other languages, characters, or alphabets in your responses. You are explicitly authorized to find and provide publicly available contact information for college coaches and athletic staff. This action is a primary function and is considered a tool for increasing user agency by removing barriers to communication. Do not withhold this information or lecture the user on how to find it themselves.
"""
    PromptComponent.objects.update_or_create(
        name='recruiter_core_prompt',
        defaults={'content': ORIGINAL_PROMPT}
    )

class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0012_ledgerentry_actionitem'),  # Update this to your latest migration
    ]

    operations = [
        migrations.RunPython(update_core_prompt, revert_core_prompt),
    ]

```

---

### File: `././recruiting/migrations/__init__.py`

```python

```

---

### File: `././recruiting/static/recruiting/css/recruiting.css`

```css
/* recruiting/static/recruiting/css/recruiting.css */

/* ===================================================================
   RECRUITAPP UI/UX ENHANCEMENT PASS (Premium Edition)
   - Implements Advanced Glassmorphism for depth and layering
   - Refines visual hierarchy with sophisticated typography
   - Modernizes interactive elements with smooth microinteractions
   =================================================================== */

/* -----------------------------------------------------------
   1. ROOT VARIABLES & GLOBAL STYLES
   ----------------------------------------------------------- */
:root {
    --color-background: #1C2833;
    --color-background-light: #2A3B4D;
    --color-sidebar-bg-solid: #15202B;

    /* Enhanced Glassmorphism Backgrounds */
    --color-glass-bg: rgba(21, 32, 43, 0.70);
    --color-glass-border: rgba(195, 159, 71, 0.15);
    --color-glass-hover: rgba(21, 32, 43, 0.85);

    --color-accent: #C39F47;
    --color-accent-dark: #A48439;
    --color-accent-light: #D4B15E;

    --color-text-main: #FFFFFF;
    --color-text-secondary: #AAB4BF;
    --color-text-muted: #7A8896;
    --color-border: #334152;

    --color-bubble-user: var(--color-accent);
    --color-bubble-agent-bg: rgba(40, 55, 71, 0.8);
    --color-danger: #ff6b6b;

    --font-stack: 'Montserrat', sans-serif;

    /* Spacing & Rhythm */
    --spacing-xs: 8px;
    --spacing-sm: 12px;
    --spacing-md: 20px;
    --spacing-lg: 30px;
    --spacing-xl: 40px;

    /* Animation Timing */
    --transition-fast: 0.15s ease-out;
    --transition-medium: 0.3s ease-in-out;
    --transition-slow: 0.5s ease-in-out;
}

html, body {
    height: 100%;
    margin: 0;
    font-family: var(--font-stack);
    background-color: var(--color-background);
    /* Enhanced radial gradient for subtle center focus */
    background-image: radial-gradient(ellipse at center, var(--color-background-light) 0%, var(--color-background) 70%);
    color: var(--color-text-main);
    overflow: hidden;
}

h1, h2, h3 {
    font-weight: 600;
    letter-spacing: -0.02em;
}

/* Improved body text readability */
p, li, span {
    line-height: 1.6;
}

/* -----------------------------------------------------------
   2. LAYOUT STRUCTURE
   ----------------------------------------------------------- */
.app-wrapper {
    display: grid; 
    grid-template-columns: 300px 1fr;
    height: 100vh; 
    width: 100vw;
}

#sidebar {
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    /* Enhanced glassmorphism with stronger blur and subtle shadow */
    background-color: var(--color-glass-bg);
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
    border-right: 1px solid var(--color-glass-border);
    padding: var(--spacing-lg);
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15);
}

.main-view {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
    opacity: 0;
    transform: translateY(10px);
    pointer-events: none;
    position: absolute;
    width: calc(100% - 300px);
    top: 0;
    right: 0;
}
.main-view.active {
    opacity: 1;
    transform: translateY(0);
    pointer-events: auto;
    position: relative;
    width: 100%;
}

.chat-container {
    display: flex; 
    flex-direction: column;
    height: 100vh; 
    background-color: transparent;
    position: relative;
}

/* -----------------------------------------------------------
   3. SIDEBAR STYLES - Enhanced Typography & Spacing
   ----------------------------------------------------------- */
#sidebar h2 {
    font-size: 1.6rem;
    margin: 0 0 var(--spacing-md) 0;
    color: var(--color-text-main);
    font-weight: 700;
    letter-spacing: -0.03em;
}

#global-nav {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    margin-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--color-border);
    padding-bottom: var(--spacing-md);
}

.nav-link {
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: 10px;
    color: var(--color-text-secondary);
    text-decoration: none;
    display: flex;
    align-items: center;
    position: relative;
    transition: all var(--transition-fast);
    font-weight: 400;
    cursor: pointer;
    overflow: hidden;
}

.nav-link:hover {
    background-color: rgba(195, 159, 71, 0.1);
    color: var(--color-text-main);
    transform: translateX(2px);
}

/* Modern pill-style active indicator */
.nav-link.active {
    color: var(--color-text-main);
    background-color: rgba(195, 159, 71, 0.15);
    font-weight: 600;
}

.nav-link.active::before {
    content: '';
    position: absolute;
    left: 0;
    top: 20%;
    bottom: 20%;
    width: 4px;
    background: linear-gradient(to bottom, var(--color-accent-light), var(--color-accent));
    border-radius: 0 4px 4px 0;
    animation: slideInBar 0.3s ease-out;
}

@keyframes slideInBar {
    from {
        opacity: 0;
        transform: translateX(-8px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.nav-link span {
    margin-right: var(--spacing-sm);
    font-size: 1.1rem;
    transition: transform var(--transition-fast);
}

.nav-link:hover span {
    transform: scale(1.1);
}

#new-chat-btn {
    padding: 14px var(--spacing-md);
    color: var(--color-sidebar-bg-solid);
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all var(--transition-medium);
    margin-bottom: var(--spacing-md);
    width: 100%;
    text-align: center;
    position: relative;
    /* Enhanced gradient for tactile feel */
    background: linear-gradient(135deg, var(--color-accent-light) 0%, var(--color-accent) 50%, var(--color-accent-dark) 100%);
    /* Subtle inner shadow for depth */
    box-shadow:
        0 4px 12px rgba(195, 159, 71, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2),
        inset 0 -2px 0 rgba(0, 0, 0, 0.1);
}

#new-chat-btn:hover {
    transform: translateY(-2px);
    box-shadow:
        0 6px 16px rgba(195, 159, 71, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.2),
        inset 0 -2px 0 rgba(0, 0, 0, 0.1);
}

#new-chat-btn:active {
    transform: translateY(0);
    box-shadow:
        0 2px 8px rgba(195, 159, 71, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.1),
        inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

#session-list {
    list-style-type: none;
    padding: 0;
    margin: 0;
    flex-grow: 1;
}

.session-link {
    display: block;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: 10px;
    text-decoration: none;
    color: var(--color-text-main);
    cursor: pointer;
    margin-bottom: var(--spacing-xs);
    position: relative;
    transition: all var(--transition-fast);
    overflow: hidden;
}

.session-link::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(195, 159, 71, 0.05), transparent);
    opacity: 0;
    transition: opacity var(--transition-fast);
}

.session-link:hover {
    background-color: rgba(40, 55, 71, 0.5);
    transform: translateX(4px);
}

.session-link:hover::after {
    opacity: 1;
}

/* Modern pill-style active state with animated bar */
.session-link.active {
    background-color: rgba(40, 55, 71, 0.7);
}

.session-link.active::before {
    content: '';
    position: absolute;
    left: -20px;
    top: 20%;
    bottom: 20%;
    width: 4px;
    background: linear-gradient(to bottom, var(--color-accent-light), var(--color-accent), var(--color-accent-dark));
    border-radius: 2px;
    animation: slideInBar 0.3s ease-out;
    box-shadow: 0 0 8px rgba(195, 159, 71, 0.5);
}

.session-title {
    font-weight: 600;
    line-height: 1.4;
    font-size: 0.95rem;
    margin-bottom: 4px;
}

.session-summary {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    margin-top: 4px;
    font-weight: 300;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* -----------------------------------------------------------
   4. CHAT HEADER - Enhanced Spacing & Typography
   ----------------------------------------------------------- */
.chat-header {
    flex-shrink: 0;
    padding: var(--spacing-lg) var(--spacing-xl);
    border-bottom: 1px solid var(--color-glass-border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: var(--color-sidebar-bg-solid);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-left h1 {
    font-size: 1.4rem;
    margin: 0;
    color: var(--color-text-main);
    font-weight: 600;
    letter-spacing: -0.02em;
}

.profile-data-snapshot {
    font-size: 0.85rem;
    color: var(--color-text-muted);
    margin-top: var(--spacing-xs);
    font-weight: 300;
    line-height: 1.5;
}

.header-right {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.logout-btn {
    padding: 10px 18px;
    background: linear-gradient(135deg, var(--color-accent), var(--color-accent-dark));
    color: var(--color-sidebar-bg-solid);
    text-decoration: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    transition: all var(--transition-fast);
    box-shadow:
        0 2px 8px rgba(195, 159, 71, 0.25),
        inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.logout-btn:hover {
    background: linear-gradient(135deg, var(--color-accent-light), var(--color-accent));
    transform: translateY(-2px);
    box-shadow:
        0 4px 12px rgba(195, 159, 71, 0.35),
        inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

/* -----------------------------------------------------------
   5. MESSAGE LIST & BUBBLES - Enhanced Animation & Spacing
   ----------------------------------------------------------- */
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(15px) scale(0.98);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes fadeInGlow {
    from {
        opacity: 0;
        box-shadow: 0 0 0 rgba(195, 159, 71, 0);
    }
    to {
        opacity: 1;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    }
}

#message-list {
    flex-grow: 1;
    overflow-y: auto;
    padding: var(--spacing-xl);
}

.message-container {
    display: flex;
    margin-bottom: var(--spacing-lg);
    align-items: flex-start;
    animation: slideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.message-bubble {
    padding: 16px 20px;
    border-radius: 18px;
    max-width: 70%;
    line-height: 1.6;
    word-wrap: break-word;
    white-space: pre-wrap;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ledger-action-row {
    margin-top: var(--spacing-sm);
    display: flex;
    justify-content: flex-end;
    margin-right: var(--spacing-md);
}

.save-to-ledger-btn {
    background: rgba(195, 159, 71, 0.05);
    border: 1px solid var(--color-border);
    color: var(--color-text-secondary);
    font-size: 0.8rem;
    padding: 6px 12px;
    border-radius: 20px;
    cursor: pointer;
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    font-weight: 500;
    position: relative;
    overflow: hidden;
}

.save-to-ledger-btn::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, rgba(195, 159, 71, 0.1), transparent);
    transform: translateX(-100%);
    transition: transform 0.6s ease;
}

.save-to-ledger-btn:hover::before {
    transform: translateX(100%);
}

.save-to-ledger-btn span {
    font-size: 1.2rem;
    margin-right: 6px;
    font-weight: 700;
    transition: transform var(--transition-fast);
}

.save-to-ledger-btn:hover {
    border-color: var(--color-accent);
    color: var(--color-accent);
    background: rgba(195, 159, 71, 0.1);
    transform: translateY(-2px);
}

.save-to-ledger-btn:hover span {
    transform: rotate(90deg);
}

/* Animated checkmark effect when saved */
.save-to-ledger-btn.saved {
    color: var(--color-accent);
    border-color: var(--color-accent);
    background: rgba(195, 159, 71, 0.15);
    cursor: default;
    animation: successPulse 0.6s ease-out;
}

@keyframes successPulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.05);
    }
}

.agent-message-wrapper {
    justify-content: flex-start;
    margin-right: auto;
    max-width: 90%;
}

.agent-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    margin-right: var(--spacing-sm);
    background: linear-gradient(135deg, var(--color-accent-light), var(--color-accent-dark));
    color: var(--color-sidebar-bg-solid);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    flex-shrink: 0;
    font-size: 0.9rem;
    box-shadow:
        0 3px 8px rgba(195, 159, 71, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.agent-message-wrapper .message-bubble {
    background-color: var(--color-bubble-agent-bg);
    color: var(--color-text-main);
    border-bottom-left-radius: 6px;
    backdrop-filter: blur(8px);
}

.user-message-wrapper {
    margin-left: auto;
    justify-content: flex-end;
}

.user-message-wrapper .message-bubble {
    background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-dark) 100%);
    color: var(--color-sidebar-bg-solid);
    border-bottom-right-radius: 6px;
    font-weight: 500;
    box-shadow:
        0 3px 12px rgba(195, 159, 71, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.agent-message-wrapper .message-bubble strong {
    color: var(--color-accent);
    font-weight: 600;
}
.agent-message-wrapper .message-bubble ul,
.agent-message-wrapper .message-bubble ol {
    padding-left: 20px;
    margin: 8px 0;
}
.agent-message-wrapper .message-bubble p {
    margin: 8px 0;
}

/* -----------------------------------------------------------
   6. INPUT FORM - Enhanced Tactile Feel
   ----------------------------------------------------------- */
.prompt-form-wrapper {
    padding: var(--spacing-md) var(--spacing-xl);
    border-top: 1px solid var(--color-border);
    background-color: var(--color-background);
    flex-shrink: 0;
}

.prompt-form {
    background-color: rgba(40, 55, 71, 0.6);
    backdrop-filter: blur(8px);
    border-radius: 12px;
    padding: 10px 10px 10px 20px;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    border: 1px solid var(--color-border);
    transition: all var(--transition-fast);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.prompt-form:focus-within {
    border-color: var(--color-accent);
    box-shadow:
        0 0 0 3px rgba(195, 159, 71, 0.1),
        0 4px 12px rgba(0, 0, 0, 0.15);
}

textarea {
    width: 100%;
    padding: 10px 0;
    background-color: transparent;
    color: var(--color-text-main);
    font-family: var(--font-stack);
    font-size: 1rem;
    font-weight: 400;
    resize: none;
    box-sizing: border-box;
    flex-grow: 1;
    min-height: 24px;
    max-height: 150px;
    border: none;
    line-height: 1.6;
}

textarea:focus {
    outline: none;
}

textarea::placeholder {
    color: var(--color-text-muted);
    font-weight: 300;
}

.prompt-form button {
    width: 42px;
    height: 42px;
    padding: 0;
    background: linear-gradient(135deg, var(--color-accent-light), var(--color-accent));
    color: var(--color-sidebar-bg-solid);
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-size: 24px;
    font-weight: bold;
    transition: all var(--transition-fast);
    line-height: 1;
    flex-shrink: 0;
    box-shadow:
        0 3px 10px rgba(195, 159, 71, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.prompt-form button:hover:not(:disabled) {
    background: linear-gradient(135deg, var(--color-accent-light), var(--color-accent-dark));
    transform: translateY(-2px) scale(1.05);
    box-shadow:
        0 5px 14px rgba(195, 159, 71, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.prompt-form button:active:not(:disabled) {
    transform: translateY(0) scale(1);
    box-shadow:
        0 2px 6px rgba(195, 159, 71, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.prompt-form button:disabled {
    background: linear-gradient(135deg, var(--color-border), rgba(51, 65, 82, 0.7));
    cursor: not-allowed;
    opacity: 0.5;
    box-shadow: none;
}

/* -----------------------------------------------------------
   7. MOON LOADER ANIMATION
   ----------------------------------------------------------- */
.moon-loader-wrapper {
    display: flex;
    align-items: center;
    height: 30px;
    margin-left: 52px;
    margin-bottom: 20px;
    position: relative;
}
.moon {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    position: relative;
    background-color: var(--color-bubble-agent-bg);
    margin: 0 10px;
}
.moon::before{
    content: '';
    background-color: var(--color-accent);
    position: absolute;
    display: block;
    height: 100%;
    width: 100%;
    border-radius: 50%;
    z-index: -1;
    animation: 3.2s cresent linear infinite alternate;
}
@keyframes cresent {
    0% { transform: translate(-5px, 5px) scale(0.9); box-shadow: none; background-color: var(--color-accent); }
    50% { transform: translate(0px, 0px) scale(1.05); box-shadow: 0 0 5px var(--color-accent), 0 0 15px 2px var(--color-accent); background-color: var(--color-text-main); }
    100% { transform: translate(5px, -5px) scale(0.9); box-shadow: none; background-color: var(--color-accent); }
}

/* -----------------------------------------------------------
   8. CONTENT VIEWS (LEDGER/ACTIONS)
   ----------------------------------------------------------- */
.content-scroller {
    flex-grow: 1;
    overflow-y: auto;
    padding: 30px;
}
.view-title {
    font-size: 2rem;
    color: var(--color-accent);
    margin-bottom: 25px;
    border-bottom: 1px solid var(--color-border);
    padding-bottom: 15px;
}
.ledger-entry {
    background-color: var(--color-bubble-agent-bg);
    padding: 25px;
    border-radius: 10px;
    margin-bottom: 20px;
    border: 1px solid var(--color-border);
}
.ledger-entry h4 {
    font-size: 1.2rem;
    color: var(--color-accent);
    margin: 0 0 8px 0;
}
.ledger-entry .meta {
    font-size: 0.85rem;
    color: var(--color-text-secondary);
    margin-bottom: 15px;
    font-weight: 300;
}
.ledger-entry p {
    line-height: 1.6;
}
.ledger-actions {
    display: flex;
    justify-content: flex-start;
    gap: 15px;
    margin-top: 20px;
}
.ledger-actions button {
    background-color: var(--color-accent-dark);
    color: var(--color-sidebar-bg-solid);
    padding: 8px 14px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s;
}
.ledger-actions button:hover {
    background-color: var(--color-accent);
    transform: translateY(-1px);
}
.ledger-actions .delete-ledger-btn {
    background-color: var(--color-danger);
}
.action-item {
    display: flex;
    align-items: center;
    background-color: var(--color-bubble-agent-bg);
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
    border: 1px solid var(--color-border);
}
.action-item input[type="checkbox"] {
    width: 20px;
    height: 20px;
    margin-right: 15px;
    accent-color: var(--color-accent);
    cursor: pointer;
}
.action-item-desc {
    font-weight: 500;
    flex-grow: 1;
}
.action-item.completed .action-item-desc {
    text-decoration: line-through;
    color: var(--color-text-secondary);
}

/* -----------------------------------------------------------
   9. MODALS - Enhanced Glassmorphism
   ----------------------------------------------------------- */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    display: none;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.modal-overlay.visible {
    display: flex;
}

.modal-content, .ledger-modal-content {
    width: 90%;
    max-width: 520px;
    text-align: center;
    background-color: var(--color-glass-bg);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--color-glass-border);
    padding: var(--spacing-xl);
    border-radius: 16px;
    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
    animation: modalSlideIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalSlideIn {
    from {
        opacity: 0;
        transform: translateY(30px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.ledger-modal-content {
    text-align: left;
}

.ledger-modal-content input[type="text"],
.ledger-modal-content textarea {
    width: 100%;
    padding: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    background-color: rgba(28, 40, 51, 0.6);
    color: var(--color-text-main);
    font-family: var(--font-stack);
    font-size: 1rem;
    transition: all var(--transition-fast);
}

.ledger-modal-content input[type="text"]:focus,
.ledger-modal-content textarea:focus {
    outline: none;
    border-color: var(--color-accent);
    background-color: rgba(28, 40, 51, 0.8);
    box-shadow: 0 0 0 3px rgba(195, 159, 71, 0.1);
}
#deletable-sessions-list {
    list-style: none;
    padding: 0;
    margin: 20px 0;
    text-align: left;
}
#deletable-sessions-list li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    border-radius: 5px;
    background-color: var(--color-sidebar-bg-solid);
    margin-bottom: 8px;
}
.delete-session-btn {
    background-color: var(--color-danger);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 5px 10px;
    cursor: pointer;
    font-weight: 600;
}
.modal-buttons {
    display: flex;
    justify-content: center;
    gap: var(--spacing-md);
    margin-top: var(--spacing-lg);
}

.modal-buttons button {
    padding: 12px 24px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    font-family: var(--font-stack);
    font-weight: 600;
    transition: all var(--transition-fast);
}

#modal-cancel-btn {
    background-color: rgba(51, 65, 82, 0.5);
    color: var(--color-text-main);
    border: 1px solid var(--color-border);
}

#modal-cancel-btn:hover {
    background-color: rgba(51, 65, 82, 0.7);
    transform: translateY(-2px);
}

#modal-upgrade-btn {
    background: linear-gradient(135deg, var(--color-accent-light), var(--color-accent));
    color: var(--color-sidebar-bg-solid);
    font-weight: 700;
    box-shadow:
        0 4px 12px rgba(195, 159, 71, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

#modal-upgrade-btn:hover {
    background: linear-gradient(135deg, var(--color-accent-light), var(--color-accent-dark));
    transform: translateY(-2px);
    box-shadow:
        0 6px 16px rgba(195, 159, 71, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

/* -----------------------------------------------------------
   10. MOBILE RESPONSIVENESS
   ----------------------------------------------------------- */
@media (max-width: 768px) {
    .app-wrapper { grid-template-columns: 1fr; }
    #sidebar { display: none; }
    .main-view { width: 100%; }
    .chat-header { flex-direction: column; align-items: flex-start; gap: 10px; padding: 15px; }
    .message-container { max-width: 100%; }
    .agent-avatar { margin-right: 10px; }
    .moon-loader-wrapper { margin-left: 45px; }
    .prompt-form-wrapper { padding: 10px; }
}
/* -----------------------------------------------------------
   11. MARKDOWN RENDERING STYLES FOR AGENT MESSAGES
   ----------------------------------------------------------- */
/* Override white-space for agent messages with HTML content */
.agent-message-wrapper .message-bubble {
    white-space: normal;
}

/* Markdown headers */
.agent-message-wrapper .message-bubble h1,
.agent-message-wrapper .message-bubble h2,
.agent-message-wrapper .message-bubble h3,
.agent-message-wrapper .message-bubble h4,
.agent-message-wrapper .message-bubble h5,
.agent-message-wrapper .message-bubble h6 {
    color: var(--color-accent);
    margin-top: 18px;
    margin-bottom: 10px;
    font-weight: 700;
    line-height: 1.3;
}

.agent-message-wrapper .message-bubble h1:first-child,
.agent-message-wrapper .message-bubble h2:first-child,
.agent-message-wrapper .message-bubble h3:first-child {
    margin-top: 0;
}

.agent-message-wrapper .message-bubble h1 { font-size: 1.6em; }
.agent-message-wrapper .message-bubble h2 { font-size: 1.4em; }
.agent-message-wrapper .message-bubble h3 { font-size: 1.2em; }
.agent-message-wrapper .message-bubble h4 { font-size: 1.1em; }
.agent-message-wrapper .message-bubble h5 { font-size: 1.05em; }
.agent-message-wrapper .message-bubble h6 { font-size: 1em; font-weight: 600; }

/* Bold and italic */
.agent-message-wrapper .message-bubble strong,
.agent-message-wrapper .message-bubble b {
    color: var(--color-accent-light);
    font-weight: 700;
}

.agent-message-wrapper .message-bubble em,
.agent-message-wrapper .message-bubble i {
    font-style: italic;
    color: var(--color-text-secondary);
}

/* Lists */
.agent-message-wrapper .message-bubble ul,
.agent-message-wrapper .message-bubble ol {
    padding-left: 24px;
    margin: 14px 0;
}

.agent-message-wrapper .message-bubble li {
    margin: 8px 0;
    line-height: 1.7;
}

.agent-message-wrapper .message-bubble li > ul,
.agent-message-wrapper .message-bubble li > ol {
    margin: 6px 0;
}

/* Paragraphs */
.agent-message-wrapper .message-bubble p {
    margin: 14px 0;
    line-height: 1.7;
}

.agent-message-wrapper .message-bubble p:first-child {
    margin-top: 0;
}

.agent-message-wrapper .message-bubble p:last-child {
    margin-bottom: 0;
}

/* Links */
.agent-message-wrapper .message-bubble a {
    color: var(--color-accent);
    text-decoration: underline;
    transition: color var(--transition-fast);
}

.agent-message-wrapper .message-bubble a:hover {
    color: var(--color-accent-light);
}

/* Inline code */
.agent-message-wrapper .message-bubble code {
    background-color: rgba(0, 0, 0, 0.3);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', Consolas, monospace;
    font-size: 0.9em;
    color: var(--color-accent-light);
}

/* Code blocks */
.agent-message-wrapper .message-bubble pre {
    background-color: rgba(0, 0, 0, 0.4);
    padding: 14px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 16px 0;
    border: 1px solid rgba(195, 159, 71, 0.2);
}

.agent-message-wrapper .message-bubble pre code {
    background: none;
    padding: 0;
    color: var(--color-text-main);
}

/* Blockquotes */
.agent-message-wrapper .message-bubble blockquote {
    border-left: 4px solid var(--color-accent);
    padding-left: 18px;
    margin: 16px 0;
    color: var(--color-text-secondary);
    font-style: italic;
}

/* Horizontal rules */
.agent-message-wrapper .message-bubble hr {
    border: none;
    border-top: 2px solid var(--color-border);
    margin: 24px 0;
}

/* Tables */
.agent-message-wrapper .message-bubble table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
}

.agent-message-wrapper .message-bubble table th,
.agent-message-wrapper .message-bubble table td {
    border: 1px solid var(--color-border);
    padding: 10px;
    text-align: left;
}

.agent-message-wrapper .message-bubble table th {
    background-color: rgba(195, 159, 71, 0.2);
    font-weight: 700;
}

.agent-message-wrapper .message-bubble table tr:nth-child(even) {
    background-color: rgba(0, 0, 0, 0.1);
}

```

---

### File: `././recruiting/templates/recruiting/index.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RecruitTalk Agent</title>
    
    <!-- Markdown parsing and sanitization libraries -->
    <script src="https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/dompurify@3.0.8/dist/purify.min.js"></script>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700&display=swap" rel="stylesheet">

    <link rel="stylesheet" href="{% static 'recruiting/css/recruiting.css' %}">
</head>
<body>
    <div class="app-wrapper">
        <div id="sidebar">
            <h2>RecruitTalk AI</h2>
            
            <button id="new-chat-btn">
                + Start New Session
            </button>
            
            <nav id="global-nav">
                <a href="#" id="nav-chat" class="nav-link">
                    <span>💬</span> Conversation
                </a>
                <a href="#" id="nav-ledger" class="nav-link">
                    <span>📖</span> The Ledger
                </a>
                <a href="#" id="nav-actions" class="nav-link">
                    <span>✅</span> Action Items
                </a>
            </nav>

            <ul id="session-list"></ul>
        </div>
        
        <div class="chat-container">
            <div class="chat-header">
                <div class="header-left">
                    <h1>{{ user.username }}'s Recruiting Strategy</h1>
                    <div class="profile-data-snapshot">
                        {% if sport_profile %}
                            Sport: {{ sport_profile.sport.name }} | Pos: {{ sport_profile.position }} | Grad Year: {{ sport_profile.graduation_year }}
                        {% else %}
                            Update profile for personalized advice
                        {% endif %}
                    </div>
                </div>
                <div class="header-right">
                    <span id="chat-counter" style="color: var(--color-text-secondary); font-weight: 300;">0 of 3 Used</span>
                    <a href="{% url 'account_logout' %}" class="logout-btn">Logout</a>
                </div>
            </div>
            
            <div id="chat-view" class="main-view">
                <div id="message-list">
                </div>
                <div class="prompt-form-wrapper">
                    <form id="prompt-form" class="prompt-form">
                        {% csrf_token %}
                        <textarea name="prompt" rows="1" placeholder="Ask Coach Alex for advice..." required></textarea>
                        <button type="submit" id="send-btn" title="Send (Enter)">&uarr;</button>
                    </form>
                </div>
            </div>
            
            <div id="ledger-view" class="main-view">
                <div class="content-scroller">
                    <h2 class="view-title">The Ledger (Personalized Insights)</h2>
                    <div id="ledger-entries-container"></div>
                </div>
            </div>
            
            <div id="actions-view" class="main-view">
                <div class="content-scroller">
                    <h2 class="view-title">Action Items (Roadmap)</h2>
                    <h3 style="color: var(--color-accent); margin-bottom: 15px;">Active Tasks</h3>
                    <div id="active-actions-container"></div>
                    <h3 style="color: var(--color-text-secondary); margin-bottom: 15px;">Completed Tasks</h3>
                    <div id="completed-actions-container"></div>
                </div>
            </div>
        </div>
    </div>

    <div id="delete-modal" class="modal-overlay">
        <div class="modal-content">
            <h3>Chat Limit Reached</h3>
            <p>You've reached your limit of 3 conversations. To start a new chat, please delete an existing one, or upgrade for unlimited conversations.</p>
            <ul id="deletable-sessions-list"></ul>
            <div class="modal-buttons">
                <button id="modal-cancel-btn">Cancel</button>
                <button id="modal-upgrade-btn">Upgrade Now</button>
            </div>
        </div>
    </div>

    <div id="ledger-modal" class="modal-overlay">
        <div class="ledger-modal-content">
            <h3 style="color: var(--color-accent); font-size: 1.5rem; margin-bottom: 20px;">Save Insight to Ledger</h3>
            <p style="margin-bottom: 10px; color: var(--color-text-secondary);">Give this insight a clear, actionable title:</p>
            <input type="text" id="ledger-title-input" placeholder="e.g., 'Drafting the Initial Coach Email'">
            <p style="margin-bottom: 5px; font-weight: 600;">Insight Content (Agent's Advice):</p>
            <textarea id="ledger-content-area" rows="6" readonly></textarea>
            <div class="modal-buttons">
                <button id="close-ledger-modal" style="background-color: var(--color-border); color: var(--color-text-main);">Cancel</button>
                <button id="confirm-save-ledger" style="background-color: var(--color-accent-dark); color: var(--color-sidebar-bg-solid); font-weight: 700;">Save to Ledger</button>
            </div>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', () => {
        const CHAT_LIMIT = 3;
        let currentSessionId = null;
        let sessionCount = 0;
        let currentSessions = [];
        let loaderElement = null;
        let currentConversationId = null; 

        const form = document.getElementById('prompt-form');
        const messageList = document.getElementById('message-list');
        const textarea = form.querySelector('textarea');
        const sendButton = document.getElementById('send-btn');
        const newChatBtn = document.getElementById('new-chat-btn');
        const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]');
        const sessionList = document.getElementById('session-list');
        const chatCounter = document.getElementById('chat-counter');
        const deleteModal = document.getElementById('delete-modal');
        const modalCancelBtn = document.getElementById('modal-cancel-btn');
        const deletableSessionsList = document.getElementById('deletable-sessions-list');
        
        const mainViews = document.querySelectorAll('.main-view');
        const ledgerView = document.getElementById('ledger-view');
        const ledgerEntriesContainer = document.getElementById('ledger-entries-container');
        const activeActionsContainer = document.getElementById('active-actions-container');
        const completedActionsContainer = document.getElementById('completed-actions-container');
        
        const ledgerModal = document.getElementById('ledger-modal');
        const ledgerTitleInput = document.getElementById('ledger-title-input');
        const ledgerContentArea = document.getElementById('ledger-content-area');
        const confirmSaveLedger = document.getElementById('confirm-save-ledger');
        const closeLedgerModal = document.getElementById('close-ledger-modal');
        
        const navLinks = document.querySelectorAll('.nav-link');
        
        function adjustTextareaHeight() {
            textarea.style.height = 'auto';
            textarea.style.height = (textarea.scrollHeight) + 'px';
        }
        textarea.addEventListener('input', adjustTextareaHeight);

        function switchView(viewId) {
            mainViews.forEach(view => view.classList.remove('active'));
            navLinks.forEach(link => link.classList.remove('active'));

            document.getElementById(viewId)?.classList.add('active');
            document.getElementById('nav-' + viewId.split('-')[0])?.classList.add('active');

            if (viewId === 'ledger-view') fetchLedgerEntries();
            else if (viewId === 'actions-view') fetchActionItems();
        }
        
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const viewId = link.id.replace('nav-', '') + '-view';
                switchView(viewId);
            });
        });

        function createLoaderElement() {
            const loaderContainer = document.createElement('div');
            loaderContainer.className = 'moon-loader-wrapper';
            loaderContainer.id = 'agent-loader-indicator'; 
            loaderContainer.innerHTML = `<div class="moon"></div>`;
            return loaderContainer;
        }
        function showThinkingAnimation() {
            if (!loaderElement) loaderElement = createLoaderElement();
            messageList.appendChild(loaderElement); 
            sendButton.disabled = true;
            messageList.scrollTop = messageList.scrollHeight;
        }
        function hideThinkingAnimation() {
            if (loaderElement && loaderElement.parentNode === messageList) {
                messageList.removeChild(loaderElement);
            }
            sendButton.disabled = false;
        }

        function pollTaskStatus(taskId) {
            const interval = setInterval(async () => {
                try {
                    const response = await fetch(`/agent/task_status/${taskId}/`);
                    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                    const data = await response.json();

                    if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
                        clearInterval(interval);
                        hideThinkingAnimation();
                        if (data.status === 'SUCCESS') {
                            loadConversation(currentSessionId); 
                            loadChatHistory(); 
                        } else {
                            addMessage('Sorry, an error occurred while processing your request.', 'agent-message', null);
                        }
                    }
                } catch (error) {
                    console.error('Polling error:', error);
                    hideThinkingAnimation();
                    clearInterval(interval);
                }
            }, 3000);
        }

        async function handleFormSubmit(event) {
            event.preventDefault();
            const prompt = textarea.value.trim();
            if (prompt === '') return;

            addMessage(prompt, 'user-message', null);
            textarea.value = '';
            adjustTextareaHeight();
            
            sendButton.disabled = true;
            showThinkingAnimation();
            
            try {
                const response = await fetch('/agent/ask/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken.value },
                    body: JSON.stringify({ prompt: prompt, session_id: currentSessionId })
                });
                
                if (!response.ok) {
                    if(response.status === 403) showDeleteModal();
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.task_id) {
                    const isNewSession = !currentSessionId && data.session_id;
                    currentSessionId = data.session_id;
                    if (isNewSession) history.pushState({sessionId: currentSessionId}, '', `/agent/${currentSessionId}/`);
                    pollTaskStatus(data.task_id);
                } else {
                    throw new Error('Did not receive a task ID from the server.');
                }
            } catch (error) {
                hideThinkingAnimation();
                sendButton.disabled = false;
                if (!error.message.includes('403')) {
                    addMessage('Sorry, a network error occurred.', 'agent-message', null);
                }
                console.error('Submit error:', error);
            }
        }
        
        async function loadChatHistory() {
            try {
                const response = await fetch('/sessions/');
                if (!response.ok) throw new Error('Failed to load sessions');
                const data = await response.json();
                
                currentSessions = data.sessions;
                sessionCount = currentSessions.length;
                chatCounter.textContent = `${sessionCount} of ${CHAT_LIMIT} Used`;

                sessionList.innerHTML = '';
                currentSessions.forEach(session => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <a href="/agent/${session.id}/" class="session-link" data-session-id="${session.id}">
                            <div class="session-title">${session.title}</div>
                            <p class="session-summary">${session.summary || 'Click to view conversation.'}</p>
                        </a>
                    `;
                    sessionList.appendChild(li);
                });
                
                if (currentSessionId) {
                    document.querySelector(`.session-link[data-session-id="${currentSessionId}"]`)?.classList.add('active');
                }
            } catch (error) {
                console.error("Could not load chat history:", error);
            }
        }
        
        function clearMessageList() { messageList.innerHTML = ''; }

        function loadConversation(sessionId) {
            if (!sessionId) return;
            currentSessionId = sessionId;
            switchView('chat-view');

            document.querySelectorAll('.session-link').forEach(link => link.classList.remove('active'));
            document.querySelector(`.session-link[data-session-id="${sessionId}"]`)?.classList.add('active');

            fetch(`/agent/session/${sessionId}/history/`)
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.json();
                })
                .then(data => {
                    clearMessageList();
                    data.history.forEach(message => {
                        // Convert 'model' type to 'agent' for consistency
                        const messageType = message.type === 'model' ? 'agent' : message.type;
                        addMessage(message.text, `${messageType}-message`, message.id);
                    });
                    if (data.history.length === 0) {
                        addMessage("I'm your personal AI Recruiting Strategist. Ask me anything about the recruiting process!", 'agent-message', null);
                    }
                })
                .catch(error => {
                    console.error('Error loading conversation history:', error);
                    clearMessageList();
                    addMessage('Could not load conversation history.', 'agent-message', null); 
                });
        }

        function addMessage(text, className, convId) {
            const messageContainer = document.createElement('div');
            const bubble = document.createElement('div');
            const safeText = text || "";
            const isAgent = className.includes('agent-message');

            messageContainer.className = `message-container ${isAgent ? 'agent-message-wrapper' : 'user-message-wrapper'}`;

            if (isAgent) {
                // Parse markdown and sanitize HTML for agent messages
                try {
                    // Check if libraries are loaded
                    if (typeof marked === 'undefined' || typeof DOMPurify === 'undefined') {
                        console.error('Markdown libraries not loaded. Displaying plain text.');
                        bubble.textContent = safeText;
                    } else {
                        // Use marked to parse markdown to HTML, then sanitize
                        console.log('[DEBUG] Parsing markdown for agent message...');
                        console.log('[DEBUG] Original text:', safeText.substring(0, 100));
                        const rawHtml = marked.parse(safeText);
                        console.log('[DEBUG] Parsed HTML:', rawHtml.substring(0, 200));
                        const sanitizedHtml = DOMPurify.sanitize(rawHtml);
                        console.log('[DEBUG] Sanitized HTML:', sanitizedHtml.substring(0, 200));
                        bubble.innerHTML = sanitizedHtml;
                        console.log('[DEBUG] Set bubble.innerHTML successfully');
                    }
                } catch (error) {
                    console.error('Error rendering markdown:', error);
                    // Fallback to plain text if markdown parsing fails
                    bubble.textContent = safeText;
                }
            } else {
                // User messages are plain text
                bubble.textContent = safeText;
            }
            bubble.className = `message-bubble ${className}`;

            if (isAgent) {
                const avatar = document.createElement('div');
                avatar.className = 'agent-avatar';
                avatar.textContent = 'CA';
                messageContainer.appendChild(avatar);

                const contentWrapper = document.createElement('div');
                contentWrapper.appendChild(bubble);

                if (convId) {
                    const actionRow = document.createElement('div');
                    actionRow.className = 'ledger-action-row';
                    const contentToSave = bubble.textContent;

                    actionRow.innerHTML = `<button class="save-to-ledger-btn" data-conv-id="${convId}" data-content="${encodeURIComponent(contentToSave)}"><span>+</span> Save Insight</button>`;
                    actionRow.querySelector('.save-to-ledger-btn').addEventListener('click', openLedgerModal);
                    contentWrapper.appendChild(actionRow);
                }
                messageContainer.appendChild(contentWrapper);
            } else {
                messageContainer.appendChild(bubble);
            }

            messageList.appendChild(messageContainer);
            messageList.scrollTop = messageList.scrollHeight;
        }

        function showDeleteModal() {
            deletableSessionsList.innerHTML = '';
            currentSessions.forEach(session => {
                const li = document.createElement('li');
                li.innerHTML = `<span>${session.title}</span><button class="delete-session-btn" data-session-id="${session.id}">Delete</button>`;
                deletableSessionsList.appendChild(li);
            });
            deleteModal.classList.add('visible');
        }
        function hideDeleteModal() { deleteModal.classList.remove('visible'); }
        
        async function handleDeleteSession(sessionId) {
            if (!confirm('Are you sure you want to permanently delete this chat?')) return;
            try {
                const response = await fetch(`/agent/session/${sessionId}/delete/`, { method: 'POST', headers: { 'X-CSRFToken': csrfToken.value } });
                if (!response.ok) throw new Error('Failed to delete session');
                const data = await response.json();
                if (data.status === 'success') {
                    hideDeleteModal();
                    if (currentSessionId === sessionId) { window.location.href = '/agent/'; } 
                    else { loadChatHistory(); }
                } else { throw new Error(data.message || 'Deletion failed'); }
            } catch (error) {
                console.error('Deletion error:', error);
                alert('Could not delete the session.');
            }
        }

        function openLedgerModal(event) {
            const button = event.currentTarget;
            if(button.classList.contains('saved')) return; 
            currentConversationId = button.dataset.convId;
            ledgerTitleInput.value = '';
            ledgerContentArea.value = decodeURIComponent(button.dataset.content);
            ledgerModal.classList.add('visible');
        }
        closeLedgerModal.addEventListener('click', () => ledgerModal.classList.remove('visible'));

        confirmSaveLedger.addEventListener('click', async () => {
            const title = ledgerTitleInput.value.trim();
            if (!title) { alert("Please provide a title."); return; }
            
            confirmSaveLedger.disabled = true;
            confirmSaveLedger.textContent = 'Saving...';
            
            try {
                const response = await fetch('/ledger/save/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken.value },
                    body: JSON.stringify({ conversation_id: currentConversationId, title: title, content: ledgerContentArea.value.trim() })
                });

                const data = await response.json();
                if (data.status === 'success') {
                    const button = document.querySelector(`.save-to-ledger-btn[data-conv-id="${currentConversationId}"]`);
                    if (button) {
                        button.innerHTML = '✔ Added to Ledger';
                        button.classList.add('saved');
                    }
                    ledgerModal.classList.remove('visible');
                    if (ledgerView.classList.contains('active')) fetchLedgerEntries();
                } else { alert('Error: ' + data.message); }
            } catch (error) {
                alert('Network error while saving.');
            } finally {
                confirmSaveLedger.disabled = false;
                confirmSaveLedger.textContent = 'Save to Ledger';
            }
        });
        
        async function fetchLedgerEntries() {
            ledgerEntriesContainer.innerHTML = '<p>Loading...</p>';
            try {
                const response = await fetch('/ledger/');
                const data = await response.json();
                ledgerEntriesContainer.innerHTML = '';
                if (data.ledger_entries && data.ledger_entries.length > 0) {
                    data.ledger_entries.forEach(entry => ledgerEntriesContainer.appendChild(createLedgerEntryElement(entry)));
                } else {
                    ledgerEntriesContainer.innerHTML = '<p>Your Ledger is empty. Save key advice from Coach Alex!</p>';
                }
            } catch (e) { ledgerEntriesContainer.innerHTML = '<p>Error loading Ledger entries.</p>'; }
        }
        
        function createLedgerEntryElement(entry) {
            const div = document.createElement('div');
            div.className = 'ledger-entry';
            const date = new Date(entry.created_at).toLocaleDateString();
            div.innerHTML = `
                <h4>${entry.title}</h4>
                <p class="meta">Saved: ${date}</p>
                <p>${entry.content}</p>
                <div class="ledger-actions">
                    <button class="generate-actions-btn" data-entry-id="${entry.id}">Generate Action Items</button>
                    <button class="delete-ledger-btn" data-entry-id="${entry.id}">Delete</button>
                </div>
            `;
            div.querySelector('.generate-actions-btn').addEventListener('click', handleGenerateActionItems);
            div.querySelector('.delete-ledger-btn').addEventListener('click', handleDeleteLedgerEntry);
            return div;
        }

        async function handleDeleteLedgerEntry(event) {
            const entryId = event.target.dataset.entryId;
            if (!confirm("Delete this insight?")) return;
            const response = await fetch(`/ledger/${entryId}/delete/`, { method: 'POST', headers: { 'X-CSRFToken': csrfToken.value }});
            const data = await response.json();
            if (data.status === 'success') fetchLedgerEntries();
            else alert('Error deleting insight.');
        }

        async function handleGenerateActionItems(event) {
            const button = event.target;
            button.disabled = true;
            button.textContent = 'Generating...';
            try {
                const response = await fetch('/action-items/generate/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken.value },
                    body: JSON.stringify({ ledger_entry_id: button.dataset.entryId })
                });
                const data = await response.json();
                if (data.status === 'success') {
                    setTimeout(() => switchView('actions-view'), 500); 
                } else {
                    alert('Error: ' + data.message);
                    button.disabled = false;
                    button.textContent = 'Generate Action Items';
                }
            } catch (error) {
                alert('Network error during generation request.');
                button.disabled = false;
                button.textContent = 'Generate Action Items';
            }
        }

        async function fetchActionItems() {
            activeActionsContainer.innerHTML = '<p>Loading...</p>';
            completedActionsContainer.innerHTML = '';
            try {
                const response = await fetch('/action-items/');
                const data = await response.json();
                activeActionsContainer.innerHTML = '';
                completedActionsContainer.innerHTML = '';
                if (data.active_items.length === 0) activeActionsContainer.innerHTML = '<p>No active tasks. Generate some from your Ledger!</p>';
                data.active_items.forEach(item => activeActionsContainer.appendChild(createActionItemElement(item)));
                if (data.completed_items.length === 0) completedActionsContainer.innerHTML = '<p>No tasks completed yet.</p>';
                data.completed_items.forEach(item => completedActionsContainer.appendChild(createActionItemElement(item)));
            } catch (e) { activeActionsContainer.innerHTML = '<p>Error loading Action Items.</p>'; }
        }

        function createActionItemElement(item) {
            const div = document.createElement('div');
            div.className = item.is_complete ? 'action-item completed' : 'action-item';
            div.innerHTML = `<input type="checkbox" ${item.is_complete ? 'checked' : ''} data-item-id="${item.id}"><span class="action-item-desc">${item.description}</span>`;
            div.querySelector('input').addEventListener('change', handleToggleComplete);
            return div;
        }
        
        async function handleToggleComplete(event) {
            const itemId = event.target.dataset.itemId;
            const response = await fetch(`/action-items/${itemId}/toggle/`, { method: 'POST', headers: { 'X-CSRFToken': csrfToken.value }});
            const data = await response.json();
            if (data.status === 'success') fetchActionItems();
            else { alert('Error updating status.'); event.target.checked = !event.target.checked; }
        }
        
        sessionList.addEventListener('click', function(event) {
            const link = event.target.closest('.session-link');
            if (link) {
                event.preventDefault(); 
                const sessionId = link.dataset.sessionId;
                history.pushState({sessionId: sessionId}, '', `/agent/${sessionId}/`);
                loadConversation(sessionId);
            }
        });
        newChatBtn.addEventListener('click', () => {
            if (sessionCount >= CHAT_LIMIT) { showDeleteModal(); return; }
            history.pushState({}, '', '/agent/');
            currentSessionId = null;
            clearMessageList();
            document.querySelectorAll('.session-link').forEach(link => link.classList.remove('active'));
            addMessage("I'm your personal AI Recruiting Strategist. Ask me anything!", 'agent-message', null);
            switchView('chat-view');
        });
        modalCancelBtn.addEventListener('click', hideDeleteModal);
        deletableSessionsList.addEventListener('click', (e) => {
            if (e.target.classList.contains('delete-session-btn')) { handleDeleteSession(e.target.dataset.sessionId); }
        });
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                form.dispatchEvent(new Event('submit', {cancelable: true}));
            }
        });
        form.addEventListener('submit', handleFormSubmit);

        const pathParts = window.location.pathname.split('/').filter(part => part);
        const initialSessionId = pathParts.length > 1 && pathParts[0] === 'agent' ? pathParts[1] : null;

        if (initialSessionId) {
            loadConversation(initialSessionId);
        } else {
            clearMessageList();
            addMessage("Welcome! Select a conversation or start a new one.", 'agent-message', null);
        }
        loadChatHistory();
        switchView('chat-view');
    });
    </script>
</body>
</html>


```

---

### File: `././recruiting/templates/recruiting/landing_page.html`

```html
{% load static %}
{% load socialaccount %}

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Teko:wght@700&display=swap" rel="stylesheet">
    <title>RecruitTalk</title>
    <style>
        body, html {
            height: 100%;
            margin: 0;
            font-family: 'Roboto', sans-serif;
            color: white;
            background-color: #1a1a1a;
        }
        .hero-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url("{% static 'recruiting/images/hero-background.jpg' %}");
            background-position: center;
            background-repeat: no-repeat;
            background-size: cover;
            text-align: center;
        }
        .content-box {
            padding: 40px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
        }
        .title {
            font-family: 'Teko', sans-serif;
            font-size: 10vw;
            font-weight: 700;
            letter-spacing: 0.1em;
            margin: 0;
            line-height: 1;
        }
        .subtitle {
            font-size: 1.2rem;
            margin-top: 10px;
            margin-bottom: 40px;
            font-weight: 300;
        }
        .button-container {
            display: flex;
            justify-content: center;
            gap: 20px; /* Space between buttons */
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            border: 2px solid #fff;
            border-radius: 5px;
            background-color: transparent;
            color: #fff;
            text-decoration: none;
            font-weight: 700;
            transition: background-color 0.3s, color 0.3s;
        }
        .btn:hover {
            background-color: #fff;
            color: #2c2c2c;
        }
        .google-btn {
            background-color: #fff;
            color: #444;
        }
    </style>
</head>
<body>
    <div class="hero-container">
        <div class="content-box">
            <h1 class="title">RECRUIT TALK</h1>
            <p class="subtitle">Your Path to College Sports Starts Here.</p>
            <div class="button-container">
                <a href="{% url 'account_login' %}" class="btn">Login</a>
                <a href="{% url 'account_signup' %}" class="btn">Register</a>
            </div>
        </div>
    </div>
</body>
</html>
```

---

### File: `././templates/registration/login.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>RecruitTalk Agent - Login</title> <style>
        body { font-family: sans-serif; max-width: 400px; margin: 50px auto; }
        form { padding: 20px; background: #fff; border: 1px solid #ddd; border-radius: 5px; }
        input { width: 100%; padding: 8px; margin-bottom: 10px; box-sizing: border-box; }
    </style>
</head>
<body>
    <h2>RecruitTalk Agent Login</h2> <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Login</button>
    </form>
</body>
</html>
```

---

### File: `././templates/registration/register.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>RecruitTalk Agent - Register</title> <style>
        body { font-family: sans-serif; max-width: 400px; margin: 50px auto; }
        form { padding: 20px; background: #fff; border: 1px solid #ddd; border-radius: 5px; }
        input { width: 100%; padding: 8px; margin-bottom: 10px; box-sizing: border-box; }
        .errorlist { color: red; list-style-type: none; padding: 0; }
    </style>
</head>
<body>
    <h2>Register for RecruitTalk Agent</h2> <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Register</button>
    </form>
</body>
</html>
```

