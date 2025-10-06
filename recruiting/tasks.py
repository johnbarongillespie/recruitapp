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