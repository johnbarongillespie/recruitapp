import os
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
        # This allows it to use the specific core_prompt for this request.
        model = GenerativeModel(
            "gemini-2.5-pro",
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