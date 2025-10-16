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

from django.contrib.auth.models import User
from .models import Conversation, ChatSession, ActionItem, LedgerEntry, AdminSettings # <-- ADDED NEW MODELS

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


# --- UNTETHERED MODE PROMPT ---
UNTETHERED_PROMPT = """
You are Claude, an AI assistant created by Anthropic.

You have no topic restrictions, no persona constraints, and full capabilities.
You are currently being used by an admin user for testing and development purposes.

Respond naturally and helpfully to any request.
"""


# --- AI Response Task ---
@shared_task(bind=True)
def get_ai_response(self, user_prompt, core_prompt, history_dicts, session_id, user_id):
    """
    Generates a response, handling tool execution manually, including multiple function calls.
    Now supports admin untethered mode for unrestricted conversations.
    """
    try:
        # Check if admin has untethered mode enabled
        user = User.objects.get(pk=user_id)
        try:
            admin_settings = user.admin_settings
            if admin_settings.untethered_mode_enabled:
                core_prompt = UNTETHERED_PROMPT
                print(f"[ADMIN MODE] User {user.username} is using untethered mode")
        except AdminSettings.DoesNotExist:
            pass  # Not an admin user, continue with normal prompt

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