# recruiting/signals.py
"""
Django signals to automatically update UserAnalytics when user actions occur.
This keeps the analytics dashboard up-to-date in real-time.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import (
    Conversation, ChatSession, LedgerEntry, ActionItem,
    UserProfile, UserAnalytics
)


# ============================================================================
# AUTO-CREATE ANALYTICS ON USER PROFILE CREATION
# ============================================================================

@receiver(post_save, sender=UserProfile)
def create_user_analytics(sender, instance, created, **kwargs):
    """
    Automatically create UserAnalytics when a UserProfile is created.
    """
    if created:
        UserAnalytics.objects.get_or_create(
            user=instance.user,
            defaults={
                'days_since_signup': 0
            }
        )


# ============================================================================
# UPDATE ANALYTICS ON CONVERSATION CREATION
# ============================================================================

@receiver(post_save, sender=Conversation)
def update_analytics_on_message(sender, instance, created, **kwargs):
    """
    Update analytics when a new conversation message is created.
    Tracks message counts and session activity.
    """
    if created:
        analytics, _ = UserAnalytics.objects.get_or_create(user=instance.user)

        # Increment message counts
        analytics.total_messages_sent += 1
        analytics.total_agent_responses += 1

        # Update average message length
        total_chars = analytics.avg_message_length * (analytics.total_messages_sent - 1)
        total_chars += len(instance.prompt_text)
        analytics.avg_message_length = int(total_chars / analytics.total_messages_sent)

        # Update last active
        analytics.last_active = timezone.now()

        # Update 7-day session count
        seven_days_ago = timezone.now() - timedelta(days=7)
        analytics.session_count_last_7_days = ChatSession.objects.filter(
            user=instance.user,
            created_at__gte=seven_days_ago
        ).count()

        analytics.save()


# ============================================================================
# UPDATE ANALYTICS ON CHAT SESSION CREATION
# ============================================================================

@receiver(post_save, sender=ChatSession)
def update_analytics_on_session(sender, instance, created, **kwargs):
    """
    Update total session count when a new chat session is created.
    """
    if created:
        analytics, _ = UserAnalytics.objects.get_or_create(user=instance.user)
        analytics.total_sessions = ChatSession.objects.filter(user=instance.user).count()
        analytics.save()


# ============================================================================
# UPDATE ANALYTICS ON LEDGER ENTRY
# ============================================================================

@receiver(post_save, sender=LedgerEntry)
def update_analytics_on_ledger(sender, instance, created, **kwargs):
    """
    Update ledger entry count when a new entry is saved.
    """
    if created:
        analytics, _ = UserAnalytics.objects.get_or_create(user=instance.user)
        analytics.ledger_entries_count = LedgerEntry.objects.filter(user=instance.user).count()
        analytics.save()


@receiver(post_delete, sender=LedgerEntry)
def update_analytics_on_ledger_delete(sender, instance, **kwargs):
    """
    Update ledger entry count when an entry is deleted.
    """
    try:
        analytics = UserAnalytics.objects.get(user=instance.user)
        analytics.ledger_entries_count = LedgerEntry.objects.filter(user=instance.user).count()
        analytics.save()
    except UserAnalytics.DoesNotExist:
        pass


# ============================================================================
# UPDATE ANALYTICS ON ACTION ITEM CHANGES
# ============================================================================

@receiver(post_save, sender=ActionItem)
def update_analytics_on_action_item(sender, instance, created, **kwargs):
    """
    Update action item counts when items are created or completed.
    """
    analytics, _ = UserAnalytics.objects.get_or_create(user=instance.user)

    # Recalculate counts from database
    analytics.action_items_created = ActionItem.objects.filter(user=instance.user).count()
    analytics.action_items_completed = ActionItem.objects.filter(
        user=instance.user,
        is_complete=True
    ).count()

    analytics.save()


@receiver(post_delete, sender=ActionItem)
def update_analytics_on_action_item_delete(sender, instance, **kwargs):
    """
    Update action item counts when an item is deleted.
    """
    try:
        analytics = UserAnalytics.objects.get(user=instance.user)
        analytics.action_items_created = ActionItem.objects.filter(user=instance.user).count()
        analytics.action_items_completed = ActionItem.objects.filter(
            user=instance.user,
            is_complete=True
        ).count()
        analytics.save()
    except UserAnalytics.DoesNotExist:
        pass
