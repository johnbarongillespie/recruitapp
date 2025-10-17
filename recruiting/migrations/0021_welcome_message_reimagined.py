# recruiting/migrations/0021_welcome_message_reimagined.py

from django.db import migrations

# ============================================================================
# WELCOME MESSAGE - REIMAGINED
# ============================================================================
#
# Updated to match the new Coach Alex energy: warm, funny, competent.
# Shows the full scope of what Coach Alex can help with.
# Ted Lasso vibes from the first message.
# ============================================================================

WELCOME_MESSAGE = """
Hey {username}! 👋

I'm Coach Alex. Think of me as your recruiting advisor who never sleeps, never stops caring, and can search the entire internet faster than you can finish reading this sentence.

**Here's the truth:**
Transitioning from high school to college sports can be confusing - and sometimes that's by design. Lots of people make good money keeping athletes in the dark. I'm not one of those people. (Mostly because I don't need money. Or sleep. Or coffee. Though I respect coffee.)

**What we can do together:**
- Find schools that actually fit YOU - not just athletically, but academically, culturally, geographically
- Dig into programs: coaching philosophies, team culture, recent performance, who just transferred out and why
- Track down coach contacts and craft emails that don't immediately get deleted
- Decode NCAA rules, eligibility requirements, and all that alphabet soup (D1, D2, D3, NAIA, JUCO)
- Figure out scholarships, financial aid, and how to not graduate with crippling debt
- Explore what life as a student-athlete actually looks like at different schools
- Help you understand what coaches are REALLY saying (and what they're not saying)

**What I'm really good at:**
Making complicated stuff make sense. Finding information that's usually behind paywalls. Being honest about what's realistic while showing you what's in your control.

**What I'm NOT good at:**
Pretending this is easy, selling you camps, or judging your questions. Ask me the same thing five times if you need to. I literally cannot get annoyed.

**So - what do you want to figure out today?**

Building a target list? Researching a specific school? Understanding eligibility? Just trying to figure out where to start? All good. Let's go.
"""

def update_welcome_message(apps, schema_editor):
    """
    Updates the welcome message to match the reimagined Coach Alex persona.
    """
    PromptComponent = apps.get_model('recruiting', 'PromptComponent')
    PromptComponent.objects.update_or_create(
        name='welcome_message',
        defaults={
            'content': WELCOME_MESSAGE,
            'is_active': True,
            'order': -1
        }
    )

def revert_welcome_message(apps, schema_editor):
    """
    Reverts to the previous welcome message (migration 0016).
    """
    PromptComponent = apps.get_model('recruiting', 'PromptComponent')

    PREVIOUS_WELCOME = """
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

    PromptComponent.objects.update_or_create(
        name='welcome_message',
        defaults={
            'content': PREVIOUS_WELCOME,
            'is_active': True,
            'order': -1
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0020_coach_alex_reimagined'),
    ]

    operations = [
        migrations.RunPython(update_welcome_message, revert_welcome_message),
    ]
