import os
import json
import vertexai
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from vertexai.generative_models import GenerativeModel, Content, Part
from .models import Conversation, ChatSession

# --- Vertex AI SDK Initialization ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=PROJECT_ID, location=LOCATION)
# ------------------------------------

@shared_task(bind=True)
def get_ai_response(self, user_prompt, core_prompt, history_dicts, session_id, user_id):
    """
    Generates a response from the Vertex AI API using the google-cloud-aiplatform SDK.
    """
    try:
        # UPDATED: Using the correct gemini-2.5-pro model
        model = GenerativeModel(
            "gemini-2.5-pro",
            system_instruction=[core_prompt]
        )
        history = [Content(role=item['role'], parts=[Part.from_text(p['text']) for p in item['parts']]) for item in history_dicts]
        
        chat = model.start_chat(history=history)
        response = chat.send_message(user_prompt)
        ai_response_text = response.text

        chat_session = ChatSession.objects.get(id=session_id)
        Conversation.objects.create(
            session=chat_session,
            user_id=user_id,
            prompt_text=user_prompt,
            response_text=ai_response_text
        )
        return ai_response_text

    except ObjectDoesNotExist:
        print(f"CRITICAL: ChatSession with ID {session_id} not found.")
        return f"Error: The specified chat session does not exist."
    except Exception as e:
        print(f"An unexpected error occurred in AI agent task: {e}. Retrying in 60s.")
        raise self.retry(exc=e, countdown=60)

@shared_task(bind=True)
def generate_title_and_summary(self, session_id):
    """
    A background task to generate a title and summary for a chat session.
    """
    try:
        session = ChatSession.objects.get(id=session_id)
        first_message = session.messages.order_by('timestamp').first()

        if not first_message:
            return "Not enough context for summary."

        conversation_context = f"USER: {first_message.prompt_text}\n\nAGENT: {first_message.response_text}"
        system_prompt = (
            "You are a summarization expert. Based on the following conversation, "
            "generate a concise title (5 words or less) and a one-sentence summary. "
            "Respond ONLY with a valid JSON object with two keys: 'title' and 'summary'."
        )
        
        # UPDATED: Using the correct gemini-2.5-pro model
        model = GenerativeModel("gemini-2.5-pro", system_instruction=[system_prompt])
        response = model.generate_content(conversation_context)
        
        cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
        response_json = json.loads(cleaned_text)
        
        new_title = response_json.get('title')
        new_summary = response_json.get('summary')

        if new_title and new_summary:
            session.title = new_title
            session.summary = new_summary
            session.save(update_fields=['title', 'summary'])
            return f"Updated session {session_id}."
        else:
            return f"Failed to extract title/summary for session {session_id}."

    except ObjectDoesNotExist:
        print(f"ERROR: Could not find ChatSession {session_id} to generate summary.")
        return f"Failed to find session {session_id}."
    except Exception as e:
        print(f"Error generating title/summary for session {session_id}: {e}")
        raise self.retry(exc=e, countdown=60)






