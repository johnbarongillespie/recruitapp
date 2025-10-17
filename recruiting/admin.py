from django.contrib import admin
from django.db.models import Count, Avg, Q
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    PromptComponent, Conversation, ChatSession, Sport, SportProfile,
    UserProfile, LedgerEntry, ActionItem, AdminSettings, UserAnalytics,
    Position, MetricDefinition, PositionProfile, PerformanceEntry, CompetitionResult
)


# ============================================================================
# ENHANCED ADMIN CLASSES WITH ANALYTICS (Milestone 3)
# ============================================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Enhanced admin for UserProfile with search, filters, and quick stats.
    """
    list_display = ['user', 'email_verified', 'has_seen_welcome', 'onboarding_complete', 'location_display']
    list_filter = ['email_verified', 'has_seen_welcome', 'onboarding_complete', 'state']
    search_fields = ['user__username', 'user__email', 'high_school', 'city', 'state']
    readonly_fields = ['user']

    def location_display(self, obj):
        """Display formatted location"""
        parts = [obj.city, obj.state, obj.zip_code]
        return ', '.join([p for p in parts if p]) or 'Not set'
    location_display.short_description = 'Location'


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """
    Enhanced admin for ChatSessions with message count and date filters.
    """
    list_display = ['title', 'user', 'message_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'user__username', 'summary']
    readonly_fields = ['id', 'created_at', 'updated_at', 'message_count']
    date_hierarchy = 'created_at'

    def message_count(self, obj):
        """Display count of messages in this session"""
        count = obj.messages.count()
        return format_html('<strong>{}</strong> messages', count)
    message_count.short_description = 'Messages'

    def get_queryset(self, request):
        """Optimize query with prefetch"""
        qs = super().get_queryset(request)
        return qs.select_related('user').prefetch_related('messages')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    Enhanced admin for individual conversations with length tracking.
    """
    list_display = ['session_title', 'user', 'prompt_preview', 'response_preview', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['prompt_text', 'response_text', 'user__username']
    readonly_fields = ['id', 'timestamp', 'prompt_length', 'response_length']
    date_hierarchy = 'timestamp'

    def session_title(self, obj):
        return obj.session.title if obj.session else 'N/A'
    session_title.short_description = 'Session'

    def prompt_preview(self, obj):
        return obj.prompt_text[:50] + '...' if len(obj.prompt_text) > 50 else obj.prompt_text
    prompt_preview.short_description = 'User Prompt'

    def response_preview(self, obj):
        return obj.response_text[:50] + '...' if len(obj.response_text) > 50 else obj.response_text
    response_preview.short_description = 'Agent Response'

    def prompt_length(self, obj):
        return f"{len(obj.prompt_text)} chars"
    prompt_length.short_description = 'Prompt Length'

    def response_length(self, obj):
        return f"{len(obj.response_text)} chars"
    response_length.short_description = 'Response Length'


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    """
    Enhanced admin for Ledger entries with title and content display.
    """
    list_display = ['title', 'user', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'title', 'content']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    content_preview.short_description = 'Content'


@admin.register(ActionItem)
class ActionItemAdmin(admin.ModelAdmin):
    """
    Enhanced admin for Action Items with completion tracking and bulk actions.
    """
    list_display = ['description_preview', 'user', 'priority_badge', 'is_complete', 'due_date', 'created_at']
    list_filter = ['is_complete', 'priority', 'created_at', 'due_date']
    search_fields = ['user__username', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    actions = ['mark_complete', 'mark_incomplete', 'set_high_priority']

    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'

    def priority_badge(self, obj):
        colors = {1: '#ff4444', 2: '#ffaa00', 3: '#44ff44'}
        labels = {1: 'HIGH', 2: 'MEDIUM', 3: 'LOW'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.priority, '#999'),
            labels.get(obj.priority, 'UNKNOWN')
        )
    priority_badge.short_description = 'Priority'

    @admin.action(description='Mark selected items as complete')
    def mark_complete(self, request, queryset):
        updated = queryset.update(is_complete=True)
        self.message_user(request, f'{updated} action items marked as complete.')

    @admin.action(description='Mark selected items as incomplete')
    def mark_incomplete(self, request, queryset):
        updated = queryset.update(is_complete=False)
        self.message_user(request, f'{updated} action items marked as incomplete.')

    @admin.action(description='Set priority to HIGH')
    def set_high_priority(self, request, queryset):
        updated = queryset.update(priority=1)
        self.message_user(request, f'{updated} action items set to HIGH priority.')


@admin.register(AdminSettings)
class AdminSettingsAdmin(admin.ModelAdmin):
    """
    Enhanced admin for AdminSettings with permission display.
    """
    list_display = ['user', 'untethered_mode_badge', 'permissions_summary', 'updated_at']
    list_filter = ['untethered_mode_enabled', 'can_view_all_user_data', 'can_modify_prompts']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']

    def untethered_mode_badge(self, obj):
        if obj.untethered_mode_enabled:
            return format_html('<span style="color: #6366f1; font-weight: bold;">🔓 ENABLED</span>')
        return format_html('<span style="color: #999;">🔒 Disabled</span>')
    untethered_mode_badge.short_description = 'Untethered Mode'

    def permissions_summary(self, obj):
        perms = []
        if obj.can_view_all_user_data:
            perms.append('View All')
        if obj.can_reset_any_user_data:
            perms.append('Reset Any')
        if obj.can_modify_prompts:
            perms.append('Edit Prompts')
        return ', '.join(perms) if perms else 'Basic'
    permissions_summary.short_description = 'Permissions'


@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    """
    Enhanced admin for UserAnalytics with comprehensive metrics display.
    """
    list_display = [
        'user',
        'total_messages_sent',
        'total_sessions',
        'ledger_entries_count',
        'action_completion_rate',
        'engagement_badge',
        'last_active'
    ]
    list_filter = ['last_active']
    search_fields = ['user__username']
    readonly_fields = [
        'created_at', 'updated_at', 'last_active',
        'total_messages_sent', 'total_agent_responses', 'total_sessions',
        'ledger_entries_count', 'action_items_created', 'action_items_completed'
    ]

    def action_completion_rate(self, obj):
        if obj.action_items_created == 0:
            return 'N/A'
        rate = (obj.action_items_completed / obj.action_items_created) * 100
        color = '#44ff44' if rate > 70 else '#ffaa00' if rate > 40 else '#ff4444'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, rate
        )
    action_completion_rate.short_description = 'Action Completion'

    def engagement_badge(self, obj):
        if obj.session_count_last_7_days >= 5:
            return format_html('<span style="color: #44ff44; font-weight: bold;">🔥 High</span>')
        elif obj.session_count_last_7_days >= 2:
            return format_html('<span style="color: #ffaa00; font-weight: bold;">📊 Medium</span>')
        else:
            return format_html('<span style="color: #999;">💤 Low</span>')
    engagement_badge.short_description = 'Engagement'


# ============================================================================
# SPORTS PROFILE ADMIN CLASSES (Milestone 5)
# ============================================================================

class PositionInline(admin.TabularInline):
    """Inline for managing positions within a sport"""
    model = Position
    extra = 0
    fields = ['code', 'name', 'abbreviation', 'category', 'display_order']
    ordering = ['display_order', 'name']


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    """Enhanced admin for Sports with position management"""
    list_display = [
        'name',
        'code',
        'position_count',
        'sport_type_badge',
        'is_active',
        'created_at'
    ]
    list_filter = ['is_active', 'has_positions', 'has_events', 'has_weight_classes', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at', 'position_count']
    inlines = [PositionInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Sport Characteristics', {
            'fields': ('has_positions', 'has_events', 'has_weight_classes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def position_count(self, obj):
        count = obj.positions.count()
        return format_html('<strong>{}</strong> positions/events', count)
    position_count.short_description = 'Positions'

    def sport_type_badge(self, obj):
        if obj.has_weight_classes:
            return format_html('<span style="background-color: #9333ea; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.85em;">Weight Classes</span>')
        elif obj.has_events:
            return format_html('<span style="background-color: #0891b2; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.85em;">Events</span>')
        elif obj.has_positions:
            return format_html('<span style="background-color: #059669; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.85em;">Positions</span>')
        return 'Individual'
    sport_type_badge.short_description = 'Type'


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """Admin for positions/events within sports"""
    list_display = ['name', 'abbreviation', 'sport', 'category', 'display_order']
    list_filter = ['sport', 'category']
    search_fields = ['name', 'code', 'abbreviation', 'sport__name']
    ordering = ['sport', 'display_order', 'name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('sport', 'name', 'code', 'abbreviation')
        }),
        ('Organization', {
            'fields': ('category', 'display_order', 'description')
        }),
    )


@admin.register(MetricDefinition)
class MetricDefinitionAdmin(admin.ModelAdmin):
    """Admin for metric definitions"""
    list_display = [
        'name',
        'code',
        'sport',
        'position',
        'metric_type_badge',
        'unit',
        'is_required',
        'is_common'
    ]
    list_filter = ['sport', 'metric_type', 'unit', 'is_required', 'is_common']
    search_fields = ['name', 'code', 'sport__name', 'position__name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('sport', 'position', 'name', 'code', 'description')
        }),
        ('Metric Properties', {
            'fields': ('metric_type', 'unit', 'is_required', 'is_common')
        }),
        ('Validation', {
            'fields': ('min_value', 'max_value'),
            'classes': ('collapse',)
        }),
        ('Display', {
            'fields': ('display_order',),
            'classes': ('collapse',)
        }),
    )

    def metric_type_badge(self, obj):
        colors = {
            'PHYSICAL': '#3b82f6',
            'PERFORMANCE': '#10b981',
            'TIME': '#f59e0b',
            'DISTANCE': '#8b5cf6',
            'PERCENTAGE': '#06b6d4',
            'COUNT': '#ec4899',
            'SCORE': '#f97316',
            'RATING': '#a855f7',
        }
        color = colors.get(obj.metric_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.85em;">{}</span>',
            color, obj.get_metric_type_display()
        )
    metric_type_badge.short_description = 'Type'


class PositionProfileInline(admin.TabularInline):
    """Inline for managing position profiles within a sport profile"""
    model = PositionProfile
    extra = 0
    fields = ['position', 'is_primary', 'proficiency_level', 'metrics']
    readonly_fields = ['metrics']


@admin.register(SportProfile)
class SportProfileAdmin(admin.ModelAdmin):
    """Enhanced admin for athlete sport profiles"""
    list_display = [
        'athlete_display',
        'sport',
        'primary_badge',
        'years_experience',
        'position_count',
        'performance_count',
        'is_active',
        'created_at'
    ]
    list_filter = ['sport', 'is_primary_sport', 'is_active', 'team_level', 'created_at']
    search_fields = [
        'user_profile__user__username',
        'user_profile__user__email',
        'sport__name',
        'current_team'
    ]
    readonly_fields = ['created_at', 'updated_at', 'position_count', 'performance_count']
    inlines = [PositionProfileInline]

    fieldsets = (
        ('Athlete & Sport', {
            'fields': ('user_profile', 'sport', 'is_primary_sport', 'is_active')
        }),
        ('Team Information', {
            'fields': ('current_team', 'team_level', 'years_experience')
        }),
        ('Statistics', {
            'fields': ('position_count', 'performance_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def athlete_display(self, obj):
        if obj.user_profile:
            username = obj.user_profile.user.username
            return format_html('<strong>{}</strong>', username)
        return 'Unknown User'
    athlete_display.short_description = 'Athlete'

    def primary_badge(self, obj):
        if obj.is_primary_sport:
            return format_html('<span style="color: #c39f47; font-weight: bold;">★ Primary</span>')
        return format_html('<span style="color: #999;">Secondary</span>')
    primary_badge.short_description = 'Status'

    def position_count(self, obj):
        count = obj.position_profiles.count()
        return format_html('<strong>{}</strong> positions', count)
    position_count.short_description = 'Positions'

    def performance_count(self, obj):
        count = obj.performances.count()
        return format_html('<strong>{}</strong> entries', count)
    performance_count.short_description = 'Performances'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user_profile__user', 'sport').prefetch_related('position_profiles')


@admin.register(PositionProfile)
class PositionProfileAdmin(admin.ModelAdmin):
    """Admin for individual position profiles"""
    list_display = [
        'athlete_display',
        'sport',
        'position',
        'primary_badge',
        'proficiency_badge',
        'has_metrics',
        'created_at'
    ]
    list_filter = ['is_primary', 'proficiency_level', 'sport_profile__sport', 'created_at']
    search_fields = [
        'sport_profile__user_profile__user__username',
        'position__name',
        'sport_profile__sport__name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'metrics_display']

    fieldsets = (
        ('Profile Information', {
            'fields': ('sport_profile', 'position', 'is_primary', 'proficiency_level')
        }),
        ('Metrics', {
            'fields': ('metrics', 'metrics_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def athlete_display(self, obj):
        if obj.sport_profile and obj.sport_profile.user_profile:
            return obj.sport_profile.user_profile.user.username
        return 'Unknown'
    athlete_display.short_description = 'Athlete'

    def sport(self, obj):
        return obj.sport_profile.sport.name if obj.sport_profile else 'N/A'
    sport.short_description = 'Sport'

    def primary_badge(self, obj):
        if obj.is_primary:
            return format_html('<span style="color: #c39f47; font-weight: bold;">★ Primary</span>')
        return format_html('<span style="color: #999;">Secondary</span>')
    primary_badge.short_description = 'Primary'

    def proficiency_badge(self, obj):
        colors = {1: '#ef4444', 2: '#f97316', 3: '#eab308', 4: '#22c55e', 5: '#10b981'}
        labels = {1: 'Beginner', 2: 'Developing', 3: 'Proficient', 4: 'Advanced', 5: 'Elite'}
        color = colors.get(obj.proficiency_level, '#6b7280')
        label = labels.get(obj.proficiency_level, 'Unknown')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.85em;">{}</span>',
            color, label
        )
    proficiency_badge.short_description = 'Proficiency'

    def has_metrics(self, obj):
        if obj.metrics:
            count = len(obj.metrics)
            return format_html('<span style="color: #10b981;">{} metrics</span>', count)
        return format_html('<span style="color: #999;">No metrics</span>')
    has_metrics.short_description = 'Metrics'

    def metrics_display(self, obj):
        if not obj.metrics:
            return 'No metrics recorded'

        output = ['<table style="width: 100%; border-collapse: collapse;">']
        output.append('<tr style="background-color: #f3f4f6;"><th style="padding: 8px; text-align: left;">Metric</th><th style="padding: 8px; text-align: left;">Value</th></tr>')

        for key, value in obj.metrics.items():
            output.append(f'<tr><td style="padding: 8px; border-top: 1px solid #e5e7eb;"><strong>{key}</strong></td><td style="padding: 8px; border-top: 1px solid #e5e7eb;">{value}</td></tr>')

        output.append('</table>')
        return format_html(''.join(output))
    metrics_display.short_description = 'Metrics Details'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('sport_profile__user_profile__user', 'sport_profile__sport', 'position')


@admin.register(PerformanceEntry)
class PerformanceEntryAdmin(admin.ModelAdmin):
    """Admin for performance tracking entries"""
    list_display = [
        'athlete_display',
        'sport',
        'date',
        'season',
        'event_name_display',
        'verified_badge',
        'metric_count',
        'created_at'
    ]
    list_filter = ['is_verified', 'sport_profile__sport', 'date', 'season', 'created_at']
    search_fields = [
        'sport_profile__user_profile__user__username',
        'event_name',
        'season',
        'notes'
    ]
    readonly_fields = ['created_at', 'updated_at', 'metrics_display']
    date_hierarchy = 'date'

    fieldsets = (
        ('Performance Details', {
            'fields': ('sport_profile', 'position_profile', 'date', 'season')
        }),
        ('Event Information', {
            'fields': ('event_name', 'opponent', 'location')
        }),
        ('Metrics & Notes', {
            'fields': ('metrics', 'metrics_display', 'notes', 'video_url')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def athlete_display(self, obj):
        if obj.sport_profile and obj.sport_profile.user_profile:
            return obj.sport_profile.user_profile.user.username
        return 'Unknown'
    athlete_display.short_description = 'Athlete'

    def sport(self, obj):
        return obj.sport_profile.sport.name if obj.sport_profile else 'N/A'
    sport.short_description = 'Sport'

    def event_name_display(self, obj):
        if obj.event_name:
            return obj.event_name[:40] + '...' if len(obj.event_name) > 40 else obj.event_name
        return format_html('<span style="color: #999;">No event name</span>')
    event_name_display.short_description = 'Event'

    def verified_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: #10b981; font-weight: bold;">✓ Verified</span>')
        return format_html('<span style="color: #f59e0b;">Pending</span>')
    verified_badge.short_description = 'Status'

    def metric_count(self, obj):
        if obj.metrics:
            count = len(obj.metrics)
            return format_html('<strong>{}</strong> metrics', count)
        return format_html('<span style="color: #999;">0 metrics</span>')
    metric_count.short_description = 'Metrics'

    def metrics_display(self, obj):
        if not obj.metrics:
            return 'No metrics recorded'

        output = ['<table style="width: 100%; border-collapse: collapse;">']
        output.append('<tr style="background-color: #f3f4f6;"><th style="padding: 8px; text-align: left;">Metric</th><th style="padding: 8px; text-align: left;">Value</th></tr>')

        for key, value in obj.metrics.items():
            output.append(f'<tr><td style="padding: 8px; border-top: 1px solid #e5e7eb;"><strong>{key}</strong></td><td style="padding: 8px; border-top: 1px solid #e5e7eb;">{value}</td></tr>')

        output.append('</table>')
        return format_html(''.join(output))
    metrics_display.short_description = 'Metrics Details'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('sport_profile__user_profile__user', 'sport_profile__sport', 'position_profile__position')


@admin.register(CompetitionResult)
class CompetitionResultAdmin(admin.ModelAdmin):
    """Admin for competition results and honors"""
    list_display = [
        'athlete_display',
        'sport',
        'competition_name',
        'result_type_badge',
        'placement',
        'date',
        'competition_level',
        'created_at'
    ]
    list_filter = ['result_type', 'competition_level', 'sport_profile__sport', 'date', 'created_at']
    search_fields = [
        'sport_profile__user_profile__user__username',
        'competition_name',
        'placement',
        'description'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'date'

    fieldsets = (
        ('Competition Information', {
            'fields': ('sport_profile', 'result_type', 'competition_name', 'competition_level', 'date')
        }),
        ('Result Details', {
            'fields': ('placement', 'description', 'significance')
        }),
        ('Documentation', {
            'fields': ('certificate_url', 'article_url'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def athlete_display(self, obj):
        if obj.sport_profile and obj.sport_profile.user_profile:
            return obj.sport_profile.user_profile.user.username
        return 'Unknown'
    athlete_display.short_description = 'Athlete'

    def sport(self, obj):
        return obj.sport_profile.sport.name if obj.sport_profile else 'N/A'
    sport.short_description = 'Sport'

    def result_type_badge(self, obj):
        colors = {
            'CHAMPIONSHIP': '#c39f47',
            'TOURNAMENT': '#3b82f6',
            'AWARD': '#8b5cf6',
            'HONOR': '#10b981',
            'RANKING': '#f59e0b',
            'RECORD': '#ec4899',
        }
        color = colors.get(obj.result_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.85em;">{}</span>',
            color, obj.get_result_type_display()
        )
    result_type_badge.short_description = 'Type'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('sport_profile__user_profile__user', 'sport_profile__sport')


# Basic registrations for simple models
admin.site.register(PromptComponent)