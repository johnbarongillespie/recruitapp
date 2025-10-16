# recruiting/migrations/0016_enhanced_welcome_message.py

from django.db import migrations

# ============================================================================
# ENHANCED WELCOME MESSAGE FOR FIRST-TIME USERS
# ============================================================================

WELCOME_MESSAGE_COMPONENT = """
**Welcome to RecruitTalk, {username}!** 👋

I'm Coach Alex, and I'm here to demystify college recruiting for you.

**What I Can Do:**
• 🔍 **Real-Time Search**: Find current coach contacts, NCAA rules, and program rankings
• 📖 **Build Your Playbook**: Save key insights to your personal Ledger
• ✅ **Create Action Plans**: Turn advice into concrete, trackable steps
• 🎯 **Strategic Guidance**: Help you navigate recruiting with confidence and agency

**Quick Start Ideas:**
• "How do I contact coaches at [school name]?"
• "What are NCAA eligibility requirements for my grad year?"
• "Help me build a target school list"
• "Show me how to write an email to a coach"

What's on your mind today?
"""

def add_welcome_component(apps, schema_editor):
    """
    Creates a separate PromptComponent for the welcome message.
    This will be injected by the view logic for first-time users.
    """
    PromptComponent = apps.get_model('recruiting', 'PromptComponent')
    PromptComponent.objects.update_or_create(
        name='welcome_message',
        defaults={
            'content': WELCOME_MESSAGE_COMPONENT,
            'is_active': True,
            'order': -1  # Negative order so it can be prepended if needed
        }
    )

def remove_welcome_component(apps, schema_editor):
    """
    Removes the welcome message component if rolling back.
    """
    PromptComponent = apps.get_model('recruiting', 'PromptComponent')
    PromptComponent.objects.filter(name='welcome_message').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0015_userprofile_has_seen_welcome'),
    ]

    operations = [
        migrations.RunPython(add_welcome_component, remove_welcome_component),
    ]
