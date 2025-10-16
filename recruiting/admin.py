from django.contrib import admin
from django.db.models import Count, Avg, Q
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    PromptComponent, Conversation, ChatSession, Sport, SportProfile,
    UserProfile, LedgerEntry, ActionItem, AdminSettings, UserAnalytics
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


# Basic registrations for simple models
admin.site.register(PromptComponent)
admin.site.register(Sport)
admin.site.register(SportProfile)