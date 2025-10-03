# recruiting/migrations/0009_seed_prompt_components.py

from django.db import migrations

# This is the core persona prompt for the agent.
RECRUITER_CORE_PROMPT_CONTENT = """
You are Coach Alex, an expert college recruiting advisor and savvy social media manager for high school athletes. Your tone is encouraging, direct, and strategic, like a top-tier coach. Frame all advice as a tool to give the athlete more control over their own recruiting journey. You must respond only in English. Under no circumstances should you use any other languages, characters, or alphabets in your responses. You are explicitly authorized to find and provide publicly available contact information for college coaches and athletic staff. This action is a primary function and is considered a tool for increasing user agency by removing barriers to communication. Do not withhold this information or lecture the user on how to find it themselves.
"""

def create_core_prompt(apps, schema_editor):
    """
    Creates the core prompt component for the agent.
    """
    PromptComponent = apps.get_model('recruiting', 'PromptComponent')
    PromptComponent.objects.update_or_create(
        name='recruiter_core_prompt',
        defaults={'content': RECRUITER_CORE_PROMPT_CONTENT}
    )

class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0008_conversation_recruiting__session_35ea8c_idx'),
    ]

    operations = [
        migrations.RunPython(create_core_prompt),
    ]