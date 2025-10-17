import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
import json
from .models import PromptComponent, Conversation, UserProfile, ChatSession, SportProfile, Sport, LedgerEntry, ActionItem, AdminSettings, FamilyAccount, FamilyMember
from .forms import CustomUserCreationForm, RoleSelectionForm
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
        # Check if this is a first-time user who needs a welcome message
        # Only do this for users who have a UserProfile (new signup flow)
        try:
            user_profile = request.user.userprofile
            if user_profile and not user_profile.has_seen_welcome:
                # Check if user has NO chat sessions at all (truly first time)
                session_count = ChatSession.objects.filter(user=request.user).count()
                if session_count == 0:
                    # Create a welcome session with the welcome message
                    welcome_session = ChatSession.objects.create(
                        user=request.user,
                        title="Welcome to RecruitApp"
                    )

                    # Get the welcome message from PromptComponent
                    try:
                        welcome_component = PromptComponent.objects.get(name='welcome_message')
                        welcome_text = welcome_component.content.format(
                            username=request.user.first_name or request.user.username
                        )

                        # Create a Conversation with the welcome message as agent's response
                        Conversation.objects.create(
                            session=welcome_session,
                            user=request.user,
                            prompt_text="",  # No user prompt for welcome message
                            response_text=welcome_text
                        )

                        # Mark that user has seen welcome
                        user_profile.has_seen_welcome = True
                        user_profile.save(update_fields=['has_seen_welcome'])

                        logger.info(f"Created welcome session for first-time user '{request.user.username}'")

                        # Redirect to the new welcome session
                        return redirect('view_session', session_id=welcome_session.id)

                    except PromptComponent.DoesNotExist:
                        logger.warning("Welcome message component not found, skipping welcome session creation")
        except UserProfile.DoesNotExist:
            # Admin/legacy users without UserProfile - skip welcome message flow
            logger.info(f"No UserProfile found for user '{request.user.username}' (admin or legacy user), skipping welcome flow")

        # Normal flow: redirect to latest session if exists
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
            # Get user's UserProfile first, then their SportProfile
            user_profile = UserProfile.objects.filter(user=request.user).first()
            if user_profile:
                profile = SportProfile.objects.select_related('sport').filter(user_profile=user_profile).first()
                if profile:
                    player_context = (
                        f"CONTEXT: You are speaking to an athlete. "
                        f"Their profile is: Sport - {profile.sport.name}. "
                        f"Use this information to personalize your advice."
                    )
        except Exception as e:
            logger.info(f"No SportProfile found for user '{request.user.username}': {e}")
            pass

        try:
            prompt_name = os.getenv('PROMPT_COMPONENT_NAME', 'recruiter_core_prompt')
            core_prompt_base = PromptComponent.objects.get(name=prompt_name).content

            # --- MODIFICATION STARTS HERE ---
            # 1. Get the current date and format it.
            current_date_str = datetime.now().strftime('%B %d, %Y')

            # 2. Create a new instruction that includes the current date.
            date_instruction = f"IMPORTANT: You must operate as if the current date is always {current_date_str}. Do not refer to this date as being in the future."

            # 3. Append UI/UX workflow knowledge if it exists
            ui_workflow_text = ""
            try:
                ui_workflow = PromptComponent.objects.get(name='ui_workflow_knowledge')
                ui_workflow_text = f"\n\n{ui_workflow.content}"
            except PromptComponent.DoesNotExist:
                logger.info("UI workflow component not found, skipping.")
                pass

            # 4. Combine the instructions to create the final core prompt.
            core_prompt = f"{date_instruction}\n\n{player_context}\n\n{core_prompt_base}{ui_workflow_text}"
            # --- MODIFICATION ENDS HERE ---

        except PromptComponent.DoesNotExist:
            logger.warning(f"PromptComponent '{prompt_name}' not found. Using fallback.")
            core_prompt = "You are a helpful AI assistant."

        history_dicts = []
        recent_conversations = chat_session.messages.select_related('user').order_by('timestamp')[:10]
        logger.info(f"[MEMORY DEBUG] Session {session_id}: Found {recent_conversations.count()} previous messages")
        for conv in recent_conversations:
            history_dicts.append({"role": "user", "parts": [{"text": conv.prompt_text}]})
            history_dicts.append({"role": "model", "parts": [{"text": conv.response_text}]})
        logger.info(f"[MEMORY DEBUG] Session {session_id}: Passing {len(history_dicts)} history entries to AI")

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
    """API endpoint to get a list of all Ledger entries for the user, separated by status."""
    entries = LedgerEntry.objects.filter(user=request.user).order_by('-created_at').values(
        'id', 'title', 'content', 'created_at', 'conversation_id', 'is_deleted'
    )
    # Split into active and deleted for front-end categorization
    active_entries = [entry for entry in entries if not entry['is_deleted']]
    deleted_entries = [entry for entry in entries if entry['is_deleted']]

    return JsonResponse({
        'ledger_entries': active_entries,
        'deleted_entries': deleted_entries
    })

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
    """API endpoint to soft delete a Ledger entry (moves to deleted section)."""
    entry = get_object_or_404(LedgerEntry, pk=entry_id, user=request.user)
    if request.method == 'POST':
        entry.is_deleted = True
        entry.save(update_fields=['is_deleted'])
        return JsonResponse({'status': 'success', 'message': 'Ledger entry moved to deleted.'})
    return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed.'}, status=405)


# ------------------------------------
# --- NEW VIEWS FOR ACTION ITEMS (Milestone 3) ---
# ------------------------------------

@login_required
def action_items_list(request):
    """API endpoint to get the list of active, completed, and deleted Action Items."""
    items = ActionItem.objects.filter(user=request.user).order_by('-created_at').values(
        'id', 'description', 'is_complete', 'is_deleted', 'priority', 'due_date', 'created_at', 'source_ledger_entry_id'
    )
    # Split into active, completed, and deleted for front-end categorization
    active_items = [item for item in items if not item['is_complete'] and not item['is_deleted']]
    completed_items = [item for item in items if item['is_complete'] and not item['is_deleted']]
    deleted_items = [item for item in items if item['is_deleted']]

    return JsonResponse({
        'active_items': active_items,
        'completed_items': completed_items,
        'deleted_items': deleted_items
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
    """API endpoint to toggle completion status of an action item."""
    item = get_object_or_404(ActionItem, pk=item_id, user=request.user)
    if request.method == 'POST':
        item.is_complete = not item.is_complete
        item.save(update_fields=['is_complete'])
        return JsonResponse({'status': 'success', 'is_complete': item.is_complete, 'message': 'Action item status updated.'})
    return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed.'}, status=405)

@login_required
def delete_action_item(request, item_id):
    """API endpoint to soft delete an action item (moves to deleted section)."""
    item = get_object_or_404(ActionItem, pk=item_id, user=request.user)
    if request.method == 'POST':
        item.is_deleted = True
        item.save(update_fields=['is_deleted'])
        return JsonResponse({'status': 'success', 'message': 'Action item moved to deleted.'})
    return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed.'}, status=405)

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
            subject = 'Activate Your RecruitApp Account'
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


# ------------------------------------
# --- DEVELOPMENT/TESTING UTILITY (REMOVE BEFORE PRODUCTION) ---
# ------------------------------------

@login_required
def reset_my_data(request):
    """
    DEVELOPMENT ONLY: Nuclear reset button to clear all user data for testing.
    This allows rapid testing of onboarding flows, welcome messages, etc.

    ⚠️ WARNING: This is DESTRUCTIVE and should be REMOVED before production deployment.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            confirmation = data.get('confirmation', '')

            # Require username confirmation to prevent accidental clicks
            if confirmation.lower() != request.user.username.lower():
                return JsonResponse({
                    'status': 'error',
                    'message': f'Confirmation failed. Type your username "{request.user.username}" to confirm.'
                }, status=400)

            # Delete all user-related data (cascade deletes handle related records)
            ChatSession.objects.filter(user=request.user).delete()
            # Conversations are cascade-deleted via ChatSession foreign key

            LedgerEntry.objects.filter(user=request.user).delete()
            ActionItem.objects.filter(user=request.user).delete()
            # SportProfile is now linked via user_profile, not user directly
            try:
                user_profile = request.user.userprofile
                SportProfile.objects.filter(user_profile=user_profile).delete()
            except UserProfile.DoesNotExist:
                pass

            # Reset UserProfile flags
            try:
                user_profile = request.user.userprofile
                user_profile.has_seen_welcome = False
                user_profile.onboarding_complete = False
                user_profile.save()
            except UserProfile.DoesNotExist:
                # Create a fresh UserProfile if it doesn't exist
                UserProfile.objects.create(user=request.user)

            logger.info(f"User '{request.user.username}' performed a complete data reset.")

            return JsonResponse({
                'status': 'success',
                'message': 'All data deleted successfully. You can now test as a fresh user.'
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            logger.error(f"Error during data reset for user {request.user.username}: {e}")
            return JsonResponse({'status': 'error', 'message': f'Reset failed: {str(e)}'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed.'}, status=405)


# ------------------------------------
# --- ADMIN FUNCTIONALITY (Milestone 3) ---
# ------------------------------------

@login_required
def toggle_untethered_mode(request):
    """
    Admin endpoint to toggle untethered mode on/off.
    Requires user to have AdminSettings.
    """
    if request.method == 'POST':
        try:
            # Check if user has admin settings
            try:
                admin_settings = request.user.admin_settings
            except AdminSettings.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Admin access required.'
                }, status=403)

            data = json.loads(request.body)
            enabled = data.get('enabled', False)

            # Update the setting
            admin_settings.untethered_mode_enabled = enabled
            admin_settings.save(update_fields=['untethered_mode_enabled'])

            logger.info(f"Admin user '{request.user.username}' {'enabled' if enabled else 'disabled'} untethered mode")

            return JsonResponse({
                'status': 'success',
                'message': f"Untethered mode {'enabled' if enabled else 'disabled'}",
                'untethered_mode_enabled': enabled
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            logger.error(f"Error toggling untethered mode for user {request.user.username}: {e}")
            return JsonResponse({'status': 'error', 'message': f'Toggle failed: {str(e)}'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed.'}, status=405)

# ------------------------------------
# --- FAMILY ACCOUNT SETUP (Milestone 4) ---
# ------------------------------------

@login_required
def role_selection(request):
    """
    Post-signup flow: User selects their role (athlete or parent).
    Creates FamilyAccount and FamilyMember based on selection.

    This view is triggered after allauth signup via the CustomSignupForm.save() method
    which sets session['needs_role_selection'] = True
    """
    # Check if user already has a family membership
    try:
        family_member = request.user.family_membership
        # User already has a role, redirect to agent
        logger.info(f"User '{request.user.username}' already has family role: {family_member.role}")
        return redirect('index')
    except FamilyMember.DoesNotExist:
        pass  # User needs to select role

    if request.method == 'POST':
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            child_first_name = form.cleaned_data.get('child_first_name', '')

            try:
                # Create FamilyAccount with user's email as primary
                family_account = FamilyAccount.objects.create(
                    primary_email=request.user.email
                )

                # Create FamilyMember to link user to family
                family_member = FamilyMember.objects.create(
                    family_account=family_account,
                    user=request.user,
                    role=role,
                    can_invite_members=(role in ['parent', 'guardian']),  # Parents can invite
                )

                # Clear session flag
                if 'needs_role_selection' in request.session:
                    del request.session['needs_role_selection']

                logger.info(f"Created FamilyAccount for '{request.user.email}' with role '{role}'")

                # Optional: Store child's first name in session for future invitation flow
                if role in ['parent', 'guardian'] and child_first_name:
                    request.session['child_first_name'] = child_first_name

                # Redirect to agent
                return redirect('index')

            except Exception as e:
                logger.error(f"Error creating family account for user {request.user.username}: {e}")
                form.add_error(None, "An error occurred creating your account. Please try again.")
    else:
        form = RoleSelectionForm()

    return render(request, 'recruiting/role_selection.html', {'form': form})
