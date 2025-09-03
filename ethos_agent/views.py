import os
import google.generativeai as genai
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from .models import PromptComponent, Conversation
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
import logging # Add this import

# Get an instance of a logger
logger = logging.getLogger(__name__)

# --- Initialization ---
# ... (rest of initialization code is the same) ...
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro-latest')


@login_required
def index(request):
    return render(request, 'ethos_agent/index.html')

@login_required
def ask_agent(request):
    if request.method == 'POST':
        # ... (core prompt loading is the same) ...
        try:
            core_prompt = PromptComponent.objects.get(name="freya_core_prompt").content
        except PromptComponent.DoesNotExist:
            core_prompt = "You are a helpful AI assistant."

        data = json.loads(request.body)
        user_prompt = data.get('prompt')

        # Add a log message
        logger.info(f"User '{request.user.username}' submitted a new prompt.")

        # ... (history building is the same) ...
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

            # Add a log message
            logger.info(f"Successfully generated AI response for user '{request.user.username}'.")

            Conversation.objects.create(
                user=request.user,
                prompt_text=user_prompt,
                response_text=ai_response_text
            )
            return JsonResponse({'response': ai_response_text})
        except Exception as e:
            # Add a critical error log message
            logger.error(f"An API error occurred for user '{request.user.username}': {e}")
            return JsonResponse({'response': f'An error occurred: {e}'})

    return JsonResponse({'response': 'Invalid request.'})

def register(request):
    # ... (register function is the same) ...
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})