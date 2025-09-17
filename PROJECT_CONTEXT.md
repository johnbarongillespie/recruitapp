# AxiomAgent Project Code Context

## Project Structure

```
./
    agent.py
    manage.py
    Procfile
    requirements.txt
    recruiting/
        admin.py
        apps.py
        forms.py
        models.py
        tests.py
        urls.py
        views.py
        __init__.py
        migrations/
            0001_initial.py
            0002_conversation.py
            0003_userprofile.py
            __init__.py
```

## File Contents

--- 

### File: `.\agent.py`

```
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Configure the API key from the environment variable
genai.configure(api_key=os.getenv("AIzaSyBjiiXWwzKGxPD0fThfOIE46E_xnMWBr1k"))

# Initialize the model we want to use
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Send our first prompt and get the response
response = model.generate_content("Give me a one-sentence greeting from a wise, newly-awakened AI that reflects the philosophy of 'RecruitTalk'.")

# Print only the text part of the AI's response
print(response.text)
```

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

### File: `.\Procfile`

```
web: gunicorn recruitapp_core.wsgi --log-file -
```

--- 

### File: `.\requirements.txt`

```
﻿annotated-types==0.7.0
asgiref==3.9.1
cachetools==5.5.2
certifi==2025.8.3
charset-normalizer==3.4.3
colorama==0.4.6
dj-database-url==3.0.1
Django==5.2.5
google-ai-generativelanguage==0.6.15
google-api-core==2.25.1
google-api-python-client==2.179.0
google-auth==2.40.3
google-auth-httplib2==0.2.0
google-generativeai==0.8.5
googleapis-common-protos==1.70.0
grpcio==1.74.0
grpcio-status==1.71.2
gunicorn==23.0.0
httplib2==0.30.0
idna==3.10
packaging==25.0
proto-plus==1.26.1
protobuf==5.29.5
psycopg2-binary==2.9.10
pyasn1==0.6.1
pyasn1_modules==0.4.2
pydantic==2.11.7
pydantic_core==2.33.2
pyparsing==3.2.3
python-dotenv==1.1.1
requests==2.32.5
rsa==4.9.1
sqlparse==0.5.3
tqdm==4.67.1
typing-inspection==0.4.1
typing_extensions==4.15.0
tzdata==2025.2
uritemplate==4.2.0
urllib3==2.5.0
whitenoise==6.9.0

```

--- 

### File: `.\recruiting\admin.py`

```
from django.contrib import admin
from .models import PromptComponent, Conversation

admin.site.register(PromptComponent)
admin.site.register(Conversation)
```

--- 

### File: `.\recruiting\apps.py`

```
from django.apps import AppConfig


class EthosAgentConfig(AppConfig):
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
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class PromptComponent(models.Model):
    # ... (this model remains the same)
    name = models.CharField(max_length=100, unique=True)
    content = models.TextField()

    def __str__(self):
        return self.name

class Conversation(models.Model):
    # ... (this model remains the same)
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt_text = models.TextField()
    response_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
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
from django.urls import path
from . import views

urlpatterns = [
    # The main page, served by the 'index' view
    path('', views.index, name='index'),
    # The new path for our AI queries, served by the 'ask_agent' view
    path('ask/', views.ask_agent, name='ask_agent'),
]
```

--- 

### File: `.\recruiting\views.py`

```
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
    return render(request, 'recruiting/index.html')

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
            
            subject = 'Activate Your RecruitTalk Agent Account'
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

### File: `.\recruiting\migrations\__init__.py`

```

```

