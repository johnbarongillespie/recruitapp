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
    has_seen_welcome = models.BooleanField(default=False)
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


# --- MILESTONE 3: ADMIN CAPABILITIES ---

class AdminSettings(models.Model):
    """
    Stores admin-specific settings and permissions.
    Allows certain users to access untethered mode and admin features.
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

# --- END NEW MODELS ---