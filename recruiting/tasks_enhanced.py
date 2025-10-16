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
