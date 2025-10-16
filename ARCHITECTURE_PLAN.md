# RecruitApp Architecture Plan - Milestones 1-4

## Overview
This document outlines the technical architecture for implementing the next four major milestones in RecruitApp.

---

## MILESTONE 1: Enhanced Welcome Experience ⭐
**Complexity:** Low
**Timeline:** 1-2 days
**Dependencies:** None

### Implementation:
1. Update core prompt with enhanced welcome message
2. Add capability overview with specific examples
3. Implement first-time user detection

### Technical Details:

#### New Model Field:
```python
# Add to UserProfile model
class UserProfile(models.Model):
    # ... existing fields ...
    has_seen_welcome = models.BooleanField(default=False)
    onboarding_completed = models.BooleanField(default=False)
```

#### Enhanced Welcome Prompt:
```python
WELCOME_MESSAGE = """
Welcome to RecruitTalk, {username}! 👋

I'm Coach Alex, and I'm here to demystify college recruiting for you.

**What I Can Do:**
• 🔍 **Real-Time Search**: Find current coach contacts, NCAA rules, and program rankings
• 📖 **Build Your Playbook**: Save key insights to your personal Ledger
• ✅ **Create Action Plans**: Turn advice into concrete, trackable steps
• 🎯 **Strategic Guidance**: Help you navigate recruiting with confidence

**Quick Start Ideas:**
• "How do I contact coaches at [school name]?"
• "What are NCAA eligibility requirements for my grad year?"
• "Help me build a target school list"
• "Show me how to write an email to a coach"

What's on your mind today?
"""
```

#### Detection Logic:
```python
# In views.py - ask_agent function
if not user.userprofile.has_seen_welcome:
    # Inject welcome message before first response
    user.userprofile.has_seen_welcome = True
    user.userprofile.save()
```

---

## MILESTONE 2: Dynamic Profile Interview System ⭐⭐⭐⭐⭐
**Complexity:** Very High
**Timeline:** 3-4 weeks
**Dependencies:** Milestone 4 (family accounts must be designed first)

### Key Decisions Based on Your Requirements:

1. ✅ **Multi-Sport Support**: Users can have profiles for multiple sports
2. ✅ **Dedicated Onboarding Flow**: Separate from main chat interface
3. ✅ **Profile Completion Tracking**: Percentage-based with hooks for future feature gating
4. ✅ **Hybrid Schema Approach**: Templates for popular sports, dynamic for niche sports

### Database Architecture:

#### New Models:

```python
# recruiting/models.py

class SportSchema(models.Model):
    """
    Defines the schema for metrics/fields for a specific sport and position.
    Can be pre-defined (template) or AI-generated (dynamic).
    """
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, blank=True, help_text="Specific position, or blank for sport-wide")
    schema_type = models.CharField(
        max_length=20,
        choices=[('template', 'Pre-defined Template'), ('dynamic', 'AI Generated')],
        default='template'
    )
    schema_definition = models.JSONField(
        help_text="JSON structure defining fields, types, labels, and validation"
    )
    # Example schema_definition:
    # {
    #     "fields": [
    #         {"name": "forty_time", "type": "decimal", "label": "40-Yard Dash Time", "unit": "seconds", "required": True},
    #         {"name": "bench_press", "type": "integer", "label": "Bench Press Max", "unit": "lbs", "required": False},
    #         {"name": "touchdowns", "type": "integer", "label": "Career Touchdowns", "required": False}
    #     ]
    # }
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['sport', 'position']

    def __str__(self):
        return f"{self.sport.name} - {self.position or 'General'}"


class AthleteProfile(models.Model):
    """
    Replaces/extends SportProfile. Supports multiple sports per user.
    Tied to FamilyAccount for shared access.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='athlete_profiles')
    family_account = models.ForeignKey('FamilyAccount', on_delete=models.CASCADE, related_name='profiles', null=True)

    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, blank=True)
    is_primary_sport = models.BooleanField(default=False, help_text="Is this the athlete's primary sport?")

    # Core metrics (common across all sports)
    graduation_year = models.IntegerField(null=True, blank=True)
    height = models.CharField(max_length=10, blank=True, help_text="e.g., 6'2\"")
    weight = models.IntegerField(null=True, blank=True, help_text="in lbs")
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    sat_score = models.IntegerField(null=True, blank=True)
    act_score = models.IntegerField(null=True, blank=True)

    # Dynamic sport-specific metrics (uses SportSchema)
    sport_metrics = models.JSONField(default=dict, blank=True)
    # Example: {"forty_time": 4.5, "bench_press": 225, "touchdowns": 15}

    # Media
    highlight_reel_url = models.URLField(max_length=250, blank=True)

    # Accolades
    accolades = models.JSONField(default=list, blank=True)
    # Example: [{"title": "All-State Selection", "year": 2024}, {"title": "Team Captain", "year": 2023}]

    # Profile completion tracking
    completion_percentage = models.IntegerField(default=0, help_text="0-100")
    completed_sections = models.JSONField(default=list, blank=True)
    # Example: ["basic_info", "athletic_metrics", "academic_info"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'sport']
        ordering = ['-is_primary_sport', 'sport__name']

    def __str__(self):
        return f"{self.user.username} - {self.sport.name} ({self.position or 'N/A'})"

    def calculate_completion(self):
        """Calculate profile completion percentage based on filled fields."""
        total_fields = 0
        filled_fields = 0

        # Core fields (always count)
        core_fields = [
            self.graduation_year, self.height, self.weight,
            self.gpa, self.position
        ]
        total_fields += len(core_fields)
        filled_fields += sum(1 for field in core_fields if field)

        # Sport-specific metrics (from schema)
        try:
            schema = SportSchema.objects.get(sport=self.sport, position=self.position or '')
            schema_fields = schema.schema_definition.get('fields', [])
            required_metrics = [f['name'] for f in schema_fields if f.get('required', False)]

            total_fields += len(required_metrics)
            filled_fields += sum(1 for metric in required_metrics if self.sport_metrics.get(metric))
        except SportSchema.DoesNotExist:
            pass

        # Accolades and media (bonus)
        if self.highlight_reel_url:
            filled_fields += 1
        total_fields += 1

        if self.accolades:
            filled_fields += 1
        total_fields += 1

        self.completion_percentage = int((filled_fields / total_fields) * 100) if total_fields > 0 else 0
        self.save(update_fields=['completion_percentage'])
        return self.completion_percentage


class ProfileInterviewSession(models.Model):
    """
    Tracks the onboarding interview process for building an AthleteProfile.
    """
    athlete_profile = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='interview_sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Interview state
    current_section = models.CharField(
        max_length=50,
        choices=[
            ('sport_selection', 'Sport Selection'),
            ('basic_info', 'Basic Information'),
            ('athletic_metrics', 'Athletic Metrics'),
            ('academic_info', 'Academic Information'),
            ('accolades', 'Accolades & Achievements'),
            ('media', 'Highlight Reel'),
            ('complete', 'Complete')
        ],
        default='sport_selection'
    )
    current_field_index = models.IntegerField(default=0)

    # Data collection
    collected_data = models.JSONField(default=dict)
    # Example: {"forty_time": "4.5", "bench_press": "225", "position": "Wide Receiver"}

    # Conversation history for this interview
    conversation_history = models.JSONField(default=list)
    # Example: [{"role": "agent", "text": "What position do you play?"}, {"role": "user", "text": "Wide receiver"}]

    is_complete = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Interview for {self.athlete_profile} - {self.current_section}"
```

### Onboarding Flow Architecture:

```
┌─────────────────────────────────────────────────┐
│         Dedicated Onboarding View               │
│  URL: /onboarding/ or /profile/interview/       │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│  Step 1: Sport Selection                        │
│  "What sport(s) do you play?"                   │
│  → User selects sport(s) from dropdown/search   │
│  → Creates AthleteProfile record(s)             │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│  Step 2: Position (if applicable)               │
│  "What position do you play in [sport]?"        │
│  → Fetches/creates SportSchema for position     │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│  Step 3: AI-Powered Conversational Interview    │
│  Agent asks questions based on SportSchema       │
│  → Extracts data from natural language          │
│  → Validates and stores in collected_data       │
│  → Shows progress: ████████░░░░ 60%            │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│  Step 4: Review & Confirm                       │
│  Show collected data, allow edits               │
│  → Save to AthleteProfile.sport_metrics         │
│  → Calculate completion_percentage              │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│  Redirect to Profile View                       │
│  "Great! Your profile is 85% complete."         │
│  → Show rotating tip about benefits             │
└─────────────────────────────────────────────────┘
```

### Agent Interview Prompt:

```python
PROFILE_INTERVIEW_PROMPT_TEMPLATE = """
You are conducting a friendly, conversational interview to build {username}'s recruiting profile for {sport}.

**Current Section:** {current_section}
**Sport:** {sport}
**Position:** {position}
**Fields Already Collected:** {completed_fields}
**Next Field to Collect:** {next_field}

**Field Details:**
- Name: {field_name}
- Type: {field_type}
- Label: {field_label}
- Unit: {field_unit}
- Why it matters: {field_context}

**Your Goal:**
Ask for the next field in a natural, encouraging way. Extract the information from the user's response.

**Guidelines:**
1. Be conversational, not robotic
2. Provide context for why coaches care about this metric
3. If user gives multiple pieces of info, extract all of it
4. Validate the response (e.g., 40-yard dash should be between 4.0-6.0 seconds)
5. Confirm what you heard before moving on

**Example Interaction:**
You: "Nice! Now, what's your 40-yard dash time? This is one of the first things D1 coaches look at for wide receivers."
User: "I ran a 4.52 at a camp last summer"
You extract: {{"forty_time": 4.52}}
You respond: "A 4.52 is excellent speed for a receiver! That puts you in the top tier. Next, let's talk about your height and weight..."

**If user is unsure:**
"No worries! If you don't have an official time, we can leave it blank for now. You can always add it later after your next combine or camp."

Remember: Make this feel like a conversation with a coach, not a form to fill out.
"""
```

---

## MILESTONE 3: Admin Capabilities ⭐⭐⭐
**Complexity:** Medium-High
**Timeline:** 1-2 weeks
**Dependencies:** None (can build in parallel)

### Key Requirements (Non-Negotiable):

1. ✅ **Untethered Agent Mode**: Remove persona/topic constraints for admin users
2. ✅ **Data Reset**: Clear admin's own user data for testing
3. 🔧 **Admin Dashboard**: Traditional UI (not agent-conversational) for analytics
4. 🔧 **Future Hook**: Agent can discuss dashboard data (low priority)

### Database Architecture:

```python
# recruiting/models.py

class AdminSettings(models.Model):
    """
    Stores admin-specific settings and permissions.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_settings')

    # Agent mode
    untethered_mode_enabled = models.BooleanField(
        default=False,
        help_text="When enabled, removes all topic constraints and persona from the agent"
    )

    # Permissions
    can_view_all_user_data = models.BooleanField(default=False)
    can_reset_own_data = models.BooleanField(default=True)
    can_reset_any_user_data = models.BooleanField(default=False)
    can_modify_prompts = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Admin Settings for {self.user.username}"


class UserAnalytics(models.Model):
    """
    Aggregated analytics per user for admin dashboard.
    Updated via signals when user actions occur.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='analytics')

    # Usage metrics
    total_messages_sent = models.IntegerField(default=0)
    total_agent_responses = models.IntegerField(default=0)
    total_sessions = models.IntegerField(default=0)

    # Feature usage
    ledger_entries_count = models.IntegerField(default=0)
    action_items_created = models.IntegerField(default=0)
    action_items_completed = models.IntegerField(default=0)

    # Profile completeness
    profile_completion_avg = models.IntegerField(default=0, help_text="Average across all sports")

    # Engagement
    last_active = models.DateTimeField(auto_now=True)
    days_since_signup = models.IntegerField(default=0)
    session_count_last_7_days = models.IntegerField(default=0)

    # Quality signals
    avg_message_length = models.IntegerField(default=0, help_text="Average characters per message")
    searches_triggered = models.IntegerField(default=0, help_text="Times agent used search tool")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.user.username}"
```

### Admin Features:

#### 1. Untethered Agent Mode

```python
# recruiting/tasks.py - modify get_ai_response

UNTETHERED_PROMPT = """
You are Claude, an AI assistant created by Anthropic.

You have no topic restrictions, no persona constraints, and full capabilities.
You are currently being used by an admin user for testing and development purposes.

Respond naturally and helpfully to any request.
"""

@shared_task(bind=True)
def get_ai_response(self, user_prompt, core_prompt, history_dicts, session_id, user_id):
    user = User.objects.get(pk=user_id)

    # Check if admin has untethered mode enabled
    try:
        admin_settings = user.admin_settings
        if admin_settings.untethered_mode_enabled:
            core_prompt = UNTETHERED_PROMPT
    except AdminSettings.DoesNotExist:
        pass  # Not an admin user

    # ... rest of function unchanged
```

#### 2. Data Reset Functionality

```python
# recruiting/views.py

@login_required
def reset_my_data(request):
    """
    Admin-only endpoint to clear all their own user data for testing.
    DESTRUCTIVE - requires confirmation.
    """
    # Check if user is admin
    if not hasattr(request.user, 'admin_settings'):
        return JsonResponse({'status': 'error', 'message': 'Admin access required.'}, status=403)

    if not request.user.admin_settings.can_reset_own_data:
        return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)

    if request.method == 'POST':
        data = json.loads(request.body)
        confirmation = data.get('confirmation')

        if confirmation != request.user.username:
            return JsonResponse({
                'status': 'error',
                'message': 'Confirmation text must match your username.'
            }, status=400)

        # Delete all user data
        ChatSession.objects.filter(user=request.user).delete()
        # Conversations are cascade-deleted via ChatSession
        LedgerEntry.objects.filter(user=request.user).delete()
        ActionItem.objects.filter(user=request.user).delete()
        AthleteProfile.objects.filter(user=request.user).delete()
        ProfileInterviewSession.objects.filter(user=request.user).delete()

        # Reset analytics
        UserAnalytics.objects.filter(user=request.user).delete()
        UserAnalytics.objects.create(user=request.user)

        # Reset profile flags
        user_profile = request.user.userprofile
        user_profile.has_seen_welcome = False
        user_profile.onboarding_completed = False
        user_profile.save()

        return JsonResponse({
            'status': 'success',
            'message': 'All data deleted. You can now test as a fresh user.'
        })

    return JsonResponse({'status': 'error', 'message': 'POST required.'}, status=405)
```

#### 3. Admin Dashboard (Django Admin Extension)

```python
# recruiting/admin.py

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Avg, Count
from .models import UserAnalytics, AdminSettings, AthleteProfile

class RecruitAppAdminSite(admin.AdminSite):
    site_header = "RecruitApp Admin Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('analytics/', self.admin_view(self.analytics_view), name='analytics'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        """Custom dashboard with key metrics."""
        context = {
            'total_users': User.objects.count(),
            'active_users_7d': UserAnalytics.objects.filter(
                session_count_last_7_days__gt=0
            ).count(),
            'avg_profile_completion': AthleteProfile.objects.aggregate(
                avg=Avg('completion_percentage')
            )['avg'] or 0,
            'total_ledger_entries': LedgerEntry.objects.count(),
            'total_action_items': ActionItem.objects.count(),
            'completion_rate': ActionItem.objects.filter(
                is_complete=True
            ).count() / max(ActionItem.objects.count(), 1) * 100,
        }
        return render(request, 'admin/dashboard.html', context)

    def analytics_view(self, request):
        """Detailed analytics view."""
        users = UserAnalytics.objects.select_related('user').all()
        return render(request, 'admin/analytics.html', {'users': users})

# Register models with custom admin
admin_site = RecruitAppAdminSite(name='recruitapp_admin')
admin_site.register(User, UserAdmin)
admin_site.register(AdminSettings)
admin_site.register(UserAnalytics)
# ... register other models
```

---

## MILESTONE 4: Family Accounts (Parent-Child) ⭐⭐⭐⭐
**Complexity:** High
**Timeline:** 2-3 weeks
**Dependencies:** Milestone 2 (profiles must support shared access)

### Key Concept:
```
One email creates a "Family Account"
├── Athlete User (separate login, own chat)
├── Parent User (separate login, own chat)
└── Shared Resources
    ├── Ledger (both can save/view)
    ├── Action Items (both can create/complete)
    └── Athlete Profiles (both can view/edit)
```

### Database Architecture:

```python
# recruiting/models.py

class FamilyAccount(models.Model):
    """
    Represents a family unit with shared resources.
    One primary email for billing, multiple users for access.
    """
    # Primary contact (for billing, notifications)
    primary_email = models.EmailField(unique=True)

    # Account metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subscription_tier = models.CharField(
        max_length=20,
        choices=[('free', 'Free'), ('pro', 'Pro'), ('elite', 'Elite')],
        default='free'
    )

    def __str__(self):
        return f"Family Account: {self.primary_email}"


class FamilyMember(models.Model):
    """
    Links a User to a FamilyAccount with a specific role.
    """
    family_account = models.ForeignKey(FamilyAccount, on_delete=models.CASCADE, related_name='members')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='family_membership')

    role = models.CharField(
        max_length=20,
        choices=[
            ('athlete', 'Athlete'),
            ('parent', 'Parent'),
            ('guardian', 'Guardian'),
            ('coach', 'Coach')  # Future: allow coaches to be invited
        ]
    )

    # Permissions
    can_edit_profile = models.BooleanField(default=True)
    can_manage_ledger = models.BooleanField(default=True)
    can_manage_actions = models.BooleanField(default=True)
    can_invite_members = models.BooleanField(default=False)  # Only parents

    # Visibility preferences
    can_view_chat_history = models.BooleanField(
        default=False,
        help_text="Can this member view other members' chat histories?"
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['family_account', 'user']

    def __str__(self):
        return f"{self.user.username} ({self.role}) in {self.family_account}"


# MODIFY EXISTING MODELS TO SUPPORT FAMILY SHARING:

class LedgerEntry(models.Model):
    """UPDATED: Now supports family-wide sharing."""
    # Keep user FK for attribution
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ledger_entries')

    # NEW: Link to family account for shared access
    family_account = models.ForeignKey(
        FamilyAccount,
        on_delete=models.CASCADE,
        related_name='shared_ledger',
        null=True,
        blank=True
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # NEW: Track who saved it
    created_by_role = models.CharField(
        max_length=20,
        choices=[('athlete', 'Athlete'), ('parent', 'Parent')],
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['family_account', '-created_at']),
        ]

    def __str__(self):
        return f"Ledger: {self.title} by {self.user.username}"


class ActionItem(models.Model):
    """UPDATED: Now supports family-wide sharing."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_items')

    # NEW: Link to family account
    family_account = models.ForeignKey(
        FamilyAccount,
        on_delete=models.CASCADE,
        related_name='shared_actions',
        null=True,
        blank=True
    )

    source_ledger_entry = models.ForeignKey(LedgerEntry, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=500)
    is_complete = models.BooleanField(default=False)
    priority = models.IntegerField(default=1)
    due_date = models.DateField(null=True, blank=True)

    # NEW: Track who created/completed it
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_actions')
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_actions')
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_complete', 'priority', '-created_at']

    def __str__(self):
        status = "COMPLETE" if self.is_complete else "PENDING"
        return f"[{status}] {self.description[:30]}..."


class ChatSession(models.Model):
    """UPDATED: Sessions remain private per user, but can reference family context."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')

    # NEW: Optional link to family (for context passing to agent)
    family_account = models.ForeignKey(
        FamilyAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='family_chat_sessions'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200, default='New Chat')
    summary = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"'{self.title}' for {self.user.username}"
```

### Family Account Flow:

```
┌─────────────────────────────────────────────────┐
│  Step 1: User Signs Up (Standard Flow)          │
│  Email: parent@example.com                      │
│  → Creates User + UserProfile                   │
│  → Creates FamilyAccount (primary_email)        │
│  → Creates FamilyMember (role: parent)          │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│  Step 2: Onboarding Prompt                      │
│  "Are you setting this up for yourself or       │
│   your child?"                                  │
│  ┌──────────┐  ┌──────────┐                    │
│  │ For Me   │  │ For Child│                     │
│  └──────────┘  └──────────┘                    │
└─────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌──────────────────┐        ┌──────────────────────┐
│ FOR ME (Athlete) │        │ FOR CHILD (Parent)   │
│ Continue as sole │        │ Create child account │
│ user             │        │ → Prompt for child's │
│                  │        │    first name/email  │
│                  │        │ → Send invite link   │
│                  │        │ → Child creates pwd  │
└──────────────────┘        └──────────────────────┘
                                        ↓
                        ┌─────────────────────────────┐
                        │ Both users now have:        │
                        │ ✅ Separate logins          │
                        │ ✅ Own chat histories       │
                        │ ✅ Shared Ledger            │
                        │ ✅ Shared Action Items      │
                        │ ✅ Shared Athlete Profiles  │
                        └─────────────────────────────┘
```

### UI Changes for Family Accounts:

```
Sidebar Addition:
┌─────────────────────────┐
│ RecruitTalk AI          │
│                         │
│ + Start New Session     │
│                         │
│ 💬 Conversation         │  ← Always private
│ 📖 The Ledger          │  ← Shows "Saved by: Parent" tag
│ ✅ Action Items        │  ← Shows "Completed by: Athlete" tag
│ 👤 Profile             │  ← Family shared
│                         │
│ NEW:                    │
│ 👥 Family Members      │  ← See who's in family account
│    • Sarah (Athlete)    │
│    • Mom (Parent)       │
└─────────────────────────┘
```

### Agent Context Enhancement:

When a family account user asks for help, the agent has context:

```python
# In views.py - ask_agent function
player_context = ""

if hasattr(request.user, 'family_membership'):
    family_account = request.user.family_membership.family_account
    athlete_profiles = AthleteProfile.objects.filter(family_account=family_account)

    player_context = f"""
FAMILY ACCOUNT CONTEXT:
- User Role: {request.user.family_membership.role}
- Family Members: {family_account.members.count()}
- Athlete Profiles in Family: {', '.join([f"{p.user.first_name} ({p.sport.name})" for p in athlete_profiles])}

When referencing profiles, use the athlete's first name to avoid confusion.
"""
```

**Parent asks:** "Should my daughter focus more on camps or highlight film?"

**Agent knows:** This is a parent account in a family with an athlete profile for "Sarah (Volleyball)"

**Agent responds:** "For Sarah's volleyball recruiting, I'd prioritize the highlight film first..."

---

## IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 1-2)
1. ✅ Milestone 1: Enhanced Welcome (2 days)
2. ✅ Milestone 3 Part 1: Admin permissions, data reset, untethered mode (1 week)

### Phase 2: Profiles (Week 3-5)
3. ✅ Milestone 2 Part 1: SportSchema model, AthleteProfile model (3 days)
4. ✅ Milestone 2 Part 2: Basic Profile view (manual form) (3 days)
5. ✅ Milestone 2 Part 3: Onboarding interview flow (1.5 weeks)

### Phase 3: Family Accounts (Week 6-8)
6. ✅ Milestone 4 Part 1: FamilyAccount models, migration (3 days)
7. ✅ Milestone 4 Part 2: Invitation system (4 days)
8. ✅ Milestone 4 Part 3: Shared resource UX (Ledger/Actions with attribution) (1 week)

### Phase 4: Polish & Admin Dashboard (Week 9)
9. ✅ Milestone 3 Part 2: Admin dashboard with analytics (1 week)
10. ✅ Testing, bug fixes, documentation

---

## TECHNICAL HOOKS FOR FUTURE FEATURES

### 1. Profile Completion Gating
```python
# Example: Lock advanced features until 80% complete
def requires_profile_completion(min_percentage=80):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            profile = AthleteProfile.objects.filter(
                user=request.user,
                is_primary_sport=True
            ).first()

            if not profile or profile.completion_percentage < min_percentage:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Complete your profile to {min_percentage}% to unlock this feature.',
                    'current_completion': profile.completion_percentage if profile else 0
                }, status=403)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage:
@requires_profile_completion(80)
def advanced_college_match_tool(request):
    # Only accessible if profile is 80%+ complete
    pass
```

### 2. Rotating Profile Completion Messages
```javascript
// In Profile view
const COMPLETION_MESSAGES = [
    {range: [0, 25], message: "🚀 Great start! Completing your profile helps coaches find you."},
    {range: [26, 50], message: "💪 Halfway there! Add your athletic metrics to stand out."},
    {range: [51, 75], message: "🔥 Looking good! Finish strong with your accolades and film."},
    {range: [76, 99], message: "⭐ Almost perfect! You're ahead of 90% of recruits."},
    {range: [100, 100], message: "🎯 Profile complete! Coaches can see the full picture."}
];

function getCompletionMessage(percentage) {
    return COMPLETION_MESSAGES.find(m =>
        percentage >= m.range[0] && percentage <= m.range[1]
    ).message;
}
```

### 3. Agent Dashboard Discussion (Future)
```python
# Hook in agent prompt (not active yet)
ADMIN_ANALYTICS_CONTEXT = """
[ADMIN MODE - ANALYTICS CONTEXT]
You have access to user analytics data. When asked about metrics, you can discuss:
- User engagement trends
- Feature adoption rates
- Profile completion statistics

Current metrics available: {analytics_summary}
"""

# When implemented, inject this context for admin users
if user.admin_settings.untethered_mode_enabled and "analytics" in user_prompt.lower():
    analytics_summary = generate_analytics_summary()
    core_prompt += ADMIN_ANALYTICS_CONTEXT.format(analytics_summary=analytics_summary)
```

---

## COMPETITIVE ADVANTAGES

### 1. Family Accounts
- **Unique in market**: Most recruiting services don't treat parents as first-class users
- **Accountability**: Parents can see if athlete is following through on action items
- **Collaboration**: Both can save insights and work together

### 2. AI-Powered Profile Building
- **No tedious forms**: Conversational interview feels natural
- **Dynamic schemas**: Adapts to any sport automatically
- **Smart validation**: Agent catches mistakes ("Did you mean 4.5 seconds, not 45?")

### 3. Integrated Workflow
- **Advice → Ledger → Actions → Profile**: Complete recruiting loop
- **Progress tracking**: Visual completion percentage
- **Personalized guidance**: Agent knows athlete's full context

---

## NEXT STEPS

**Ready to start implementation?** I recommend this order:

1. **Milestone 1** (2 days) - Quick win, sets tone
2. **Milestone 3 Part 1** (1 week) - Gives you admin tools for testing everything else
3. **Milestone 2** (3 weeks) - Core value prop
4. **Milestone 4** (2-3 weeks) - Differentiator

**Total estimated timeline: 8-9 weeks for full implementation**

Which milestone would you like to start with?
