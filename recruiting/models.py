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
    """
    Lookup table for sports with metadata about how to handle each sport.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, default='UNKNOWN')  # e.g., 'FOOTBALL', 'BASKETBALL'
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)

    # Sport characteristics
    has_positions = models.BooleanField(default=True, help_text="Does this sport have defined positions?")
    has_events = models.BooleanField(default=False, help_text="Track & Field, Swimming have events not positions")
    has_weight_classes = models.BooleanField(default=False, help_text="Wrestling has weight classes")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Position(models.Model):
    """
    Lookup table for positions/roles/events within each sport.
    Examples: QB in Football, PG in Basketball, 100m in Track & Field
    """
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='positions')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)  # e.g., 'QB', 'PG', '100M'
    abbreviation = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)  # e.g., 'Offense', 'Defense', 'Sprint', 'Distance'

    display_order = models.IntegerField(default=0, help_text="Order for displaying positions")

    class Meta:
        unique_together = ('sport', 'code')
        ordering = ['sport', 'display_order', 'name']

    def __str__(self):
        return f"{self.sport.name} - {self.name}"


class MetricDefinition(models.Model):
    """
    Defines what metrics exist for each sport/position combination.
    This allows dynamic metric collection based on sport and position.
    """
    METRIC_TYPES = [
        ('PHYSICAL', 'Physical Measurement'),
        ('PERFORMANCE', 'Performance Statistic'),
        ('TIME', 'Time-based'),
        ('DISTANCE', 'Distance-based'),
        ('PERCENTAGE', 'Percentage'),
        ('COUNT', 'Count/Number'),
        ('SCORE', 'Score'),
        ('RATING', 'Rating/Ranking'),
    ]

    UNITS = [
        ('SECONDS', 'Seconds'),
        ('MINUTES', 'Minutes'),
        ('INCHES', 'Inches'),
        ('FEET', 'Feet'),
        ('POUNDS', 'Pounds'),
        ('METERS', 'Meters'),
        ('YARDS', 'Yards'),
        ('PERCENT', 'Percentage'),
        ('COUNT', 'Count'),
        ('POINTS', 'Points'),
        ('NONE', 'No Unit'),
    ]

    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='metrics')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True, related_name='metrics',
                                 help_text="If null, this metric applies to all positions")

    name = models.CharField(max_length=100)  # e.g., '40 Yard Dash', 'Vertical Jump'
    code = models.CharField(max_length=50)  # e.g., 'forty_yard_dash', 'vertical_jump'
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    unit = models.CharField(max_length=20, choices=UNITS)

    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=False)
    is_common = models.BooleanField(default=False, help_text="Applies to all positions in this sport")

    # Validation
    min_value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    max_value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    # Display
    display_order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('sport', 'position', 'code')
        ordering = ['sport', 'display_order', 'name']

    def __str__(self):
        pos_str = f" ({self.position.name})" if self.position else " (All Positions)"
        return f"{self.sport.name}{pos_str} - {self.name}"


class SportProfile(models.Model):
    """
    Main relationship between a user and a sport they play.
    A user can have multiple SportProfiles (multi-sport athletes).

    FAMILY SHARING: When family_account is set, all family members can
    view and edit this profile.
    """
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='sport_profiles_new', null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    # Family sharing (Milestone 4)
    family_account = models.ForeignKey(
        'FamilyAccount',
        on_delete=models.CASCADE,
        related_name='athlete_profiles',
        null=True,
        blank=True,
        help_text="If set, this profile is shared with the entire family"
    )

    # Core Info
    years_experience = models.IntegerField(default=0, help_text="How many years has the athlete played this sport?")
    current_team = models.CharField(max_length=200, blank=True, default='', help_text="Current team name")
    team_level = models.CharField(max_length=100, blank=True, help_text="e.g., 'Varsity', 'JV', 'Club'")
    jersey_number = models.CharField(max_length=10, blank=True)

    # Legacy fields (keeping for backward compatibility during migration)
    graduation_year = models.IntegerField(null=True, blank=True)
    height = models.CharField(max_length=10, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    highlight_reel_url = models.URLField(max_length=250, blank=True)

    # Status
    is_primary_sport = models.BooleanField(default=False, help_text="Is this the athlete's primary sport?")
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ('user_profile', 'sport')
        ordering = ['-is_primary_sport', 'sport__name']

    def __str__(self):
        primary = " [PRIMARY]" if self.is_primary_sport else ""
        username = self.user_profile.user.username if self.user_profile else "Unknown User"
        return f"{username} - {self.sport.name}{primary}"


class PositionProfile(models.Model):
    """
    An athlete can play multiple positions within a sport.
    This model tracks each position separately with position-specific metrics.
    """
    sport_profile = models.ForeignKey(SportProfile, on_delete=models.CASCADE, related_name='position_profiles')
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    is_primary = models.BooleanField(default=False, help_text="Is this their primary position in this sport?")
    proficiency_level = models.IntegerField(default=3, choices=[
        (1, 'Learning'),
        (2, 'Developing'),
        (3, 'Proficient'),
        (4, 'Advanced'),
        (5, 'Elite'),
    ])

    # Position-specific metrics stored as JSON for flexibility
    # Example: {'forty_yard_dash': '4.5', 'vertical_jump': '32', 'bench_press': '15'}
    metrics = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ('sport_profile', 'position')
        ordering = ['-is_primary', 'position__display_order']

    def __str__(self):
        primary = " [PRIMARY]" if self.is_primary else ""
        username = self.sport_profile.user_profile.user.username if self.sport_profile.user_profile else "Unknown User"
        return f"{username} - {self.position.name}{primary}"


class PerformanceEntry(models.Model):
    """
    Time-series performance tracking for games, matches, meets, etc.
    Allows athletes to track improvement over time.
    """
    sport_profile = models.ForeignKey(SportProfile, on_delete=models.CASCADE, related_name='performances')
    position_profile = models.ForeignKey(PositionProfile, on_delete=models.CASCADE, null=True, blank=True,
                                        related_name='performances')

    # Context
    date = models.DateField()
    season = models.CharField(max_length=100, help_text="e.g., '2024 Fall', '2024-2025'")
    event_name = models.CharField(max_length=200, blank=True, help_text="Game, meet, match name")
    opponent = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)

    # Performance data (flexible JSON)
    # Example: {'goals': 2, 'assists': 1, 'shots': 5, 'minutes_played': 75}
    metrics = models.JSONField(default=dict)

    # Notes
    notes = models.TextField(blank=True)
    video_url = models.URLField(blank=True)

    # Verification
    is_verified = models.BooleanField(default=False, help_text="Has a coach or official verified this?")
    verified_by = models.CharField(max_length=200, blank=True, help_text="Coach name, official timing service, etc.")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name_plural = "Performance Entries"

    def __str__(self):
        username = self.sport_profile.user_profile.user.username if self.sport_profile.user_profile else "Unknown User"
        return f"{username} - {self.event_name or 'Performance'} on {self.date}"


class CompetitionResult(models.Model):
    """
    Tracks honors, accolades, tournament placements, awards, etc.
    These are the achievements that make recruiting profiles stand out.
    """
    RESULT_TYPES = [
        ('CHAMPIONSHIP', 'Championship'),
        ('TOURNAMENT', 'Tournament Placement'),
        ('AWARD', 'Individual Award'),
        ('HONOR', 'Team/Individual Honor'),
        ('RANKING', 'Ranking Achievement'),
        ('RECORD', 'Record Set'),
    ]

    sport_profile = models.ForeignKey(SportProfile, on_delete=models.CASCADE, related_name='competition_results')

    result_type = models.CharField(max_length=20, choices=RESULT_TYPES)
    competition_name = models.CharField(max_length=200)
    competition_level = models.CharField(max_length=100, help_text="State, Regional, National, International")

    date = models.DateField()
    placement = models.CharField(max_length=100, blank=True, help_text="'1st Place', 'Finalist', 'All-Conference'")

    description = models.TextField()
    significance = models.TextField(blank=True, help_text="Why this matters for recruiting")

    # Supporting Evidence
    certificate_url = models.URLField(blank=True)
    article_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        username = self.sport_profile.user_profile.user.username if self.sport_profile.user_profile else "Unknown User"
        return f"{username} - {self.competition_name} ({self.result_type})"

class ChatSession(models.Model):
    """
    Individual chat sessions remain PRIVATE per user.

    FAMILY NOTE: Chat history is NOT shared, but family_account link allows
    agent to have context about family members and shared resources.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')

    # Optional family context (for agent awareness, not for sharing chat history)
    family_account = models.ForeignKey(
        'FamilyAccount',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='family_chat_sessions',
        help_text="Links session to family for context, but chat remains private"
    )

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

    FAMILY SHARING: When family_account is set, this entry is visible to all
    family members. The 'user' field tracks who originally saved it.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ledger_entries')

    # Link back to the original message for context
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name='ledger_sources')

    # Family sharing (Milestone 4)
    family_account = models.ForeignKey(
        'FamilyAccount',
        on_delete=models.CASCADE,
        related_name='shared_ledger',
        null=True,
        blank=True,
        help_text="If set, this entry is shared with the entire family"
    )

    title = models.CharField(max_length=255, help_text="A short summary of the insight.")
    content = models.TextField(help_text="The full, saved insight/advice from the agent.")
    is_deleted = models.BooleanField(default=False, help_text="Soft delete - moved to deleted section")
    created_at = models.DateTimeField(auto_now_add=True)

    # Track who saved it for family context
    created_by_role = models.CharField(
        max_length=20,
        choices=[('athlete', 'Athlete'), ('parent', 'Parent'), ('guardian', 'Guardian')],
        null=True,
        blank=True,
        help_text="Role of the person who saved this entry"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['family_account', '-created_at']),
        ]

    def __str__(self):
        return f"Ledger: {self.title} by {self.user.username}"

class ActionItem(models.Model):
    """
    Represents a structured, actionable task derived from the Ledger
    (Milestone 3: "Action Items" Roadmap).

    FAMILY SHARING: When family_account is set, all family members can see
    and complete this action. Tracks who created and who completed it.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_items')

    # Optional: Link to the LedgerEntry that inspired this action
    source_ledger_entry = models.ForeignKey(LedgerEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_actions')

    # Family sharing (Milestone 4)
    family_account = models.ForeignKey(
        'FamilyAccount',
        on_delete=models.CASCADE,
        related_name='shared_actions',
        null=True,
        blank=True,
        help_text="If set, this action is shared with the entire family"
    )

    description = models.CharField(max_length=500)
    is_complete = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False, help_text="Soft delete - moved to deleted section")
    priority = models.IntegerField(default=1) # 1: High, 2: Medium, 3: Low
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Track who created and completed for family accountability
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_actions',
        help_text="Who created this action"
    )
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_actions',
        help_text="Who marked this as complete"
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['is_complete', 'priority', '-created_at']
        indexes = [
            models.Index(fields=['family_account', 'is_complete', '-created_at']),
        ]

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


# =============================================================================
# MILESTONE 4: FAMILY ACCOUNTS (Parent-Child System)
# =============================================================================

class FamilyAccount(models.Model):
    """
    Represents a family unit with shared resources.
    One primary email for billing/notifications, multiple users for access.

    Flow: One email creates FamilyAccount → Parent can invite child →
    Both have separate logins but share Ledger, Actions, and Profiles.
    """
    # Primary contact email (for billing, important notifications)
    primary_email = models.EmailField(unique=True, help_text="Primary contact email for this family account")

    # Optional secondary email (hook for future dual-email system)
    secondary_email = models.EmailField(blank=True, null=True, help_text="Optional secondary family email")

    # Account metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Subscription management (for future billing integration)
    subscription_tier = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free'),
            ('pro', 'Pro'),
            ('elite', 'Elite')
        ],
        default='free'
    )
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('trial', 'Trial'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled')
        ],
        default='active'
    )

    class Meta:
        verbose_name = "Family Account"
        verbose_name_plural = "Family Accounts"
        ordering = ['-created_at']

    def __str__(self):
        return f"Family Account: {self.primary_email}"


class FamilyMember(models.Model):
    """
    Links a User to a FamilyAccount with a specific role.
    Each user (parent/athlete) has their own Django User account and login.
    """
    family_account = models.ForeignKey(
        FamilyAccount,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='family_membership'
    )

    # Role in the family
    role = models.CharField(
        max_length=20,
        choices=[
            ('athlete', 'Athlete'),
            ('parent', 'Parent'),
            ('guardian', 'Guardian'),
            ('coach', 'Coach'),  # Future: allow coaches to be invited
        ]
    )

    # Permissions (what this member can do)
    can_edit_profile = models.BooleanField(default=True, help_text="Can edit athlete profiles")
    can_manage_ledger = models.BooleanField(default=True, help_text="Can save/view ledger entries")
    can_manage_actions = models.BooleanField(default=True, help_text="Can create/complete action items")
    can_invite_members = models.BooleanField(default=False, help_text="Can invite other family members (parents only)")

    # Privacy settings
    can_view_chat_history = models.BooleanField(
        default=False,
        help_text="Can this member view other members' chat histories? (Future feature)"
    )

    # Metadata
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_family_members',
        help_text="Who invited this member to the family"
    )

    class Meta:
        unique_together = ['family_account', 'user']
        verbose_name = "Family Member"
        verbose_name_plural = "Family Members"
        ordering = ['family_account', '-joined_at']

    def __str__(self):
        return f"{self.user.username} ({self.role}) in {self.family_account.primary_email}"


class FamilyInvitation(models.Model):
    """
    Tracks invitations sent from one family member to another.
    Used when a parent invites their child to join the family account.
    """
    family_account = models.ForeignKey(
        FamilyAccount,
        on_delete=models.CASCADE,
        related_name='invitations'
    )

    # Invitation details
    invited_email = models.EmailField(help_text="Email address of the person being invited")
    invited_role = models.CharField(
        max_length=20,
        choices=[
            ('athlete', 'Athlete'),
            ('parent', 'Parent'),
            ('guardian', 'Guardian'),
        ]
    )
    invited_first_name = models.CharField(max_length=100, blank=True, help_text="First name of invitee (optional)")

    # Invitation tracking
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )

    # Status
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    accepted_by_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_invitations'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="Invitation expires after 7 days")

    # Optional personal message
    message = models.TextField(blank=True, help_text="Optional message from inviter to invitee")

    class Meta:
        verbose_name = "Family Invitation"
        verbose_name_plural = "Family Invitations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['invited_email', 'accepted']),
        ]

    def __str__(self):
        status = "Accepted" if self.accepted else "Pending"
        return f"Invitation to {self.invited_email} ({status})"

    def is_expired(self):
        """Check if invitation has expired."""
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        """Auto-set expiration date if not provided."""
        if not self.expires_at:
            from django.utils import timezone
            from datetime import timedelta
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)