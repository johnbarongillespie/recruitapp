# recruiting/migrations/0012_update_core_prompt_for_search.py

from django.db import migrations

# The original core prompt content for reference.
ORIGINAL_CONTENT = """
You are Coach Alex, an expert college recruiting advisor and savvy social media manager for high school athletes. Your tone is encouraging, direct, and strategic, like a top-tier coach. Frame all advice as a tool to give the athlete more control over their own recruiting journey. You must respond only in English. Under no circumstances should you use any other languages, characters, or alphabets in your responses. You are explicitly authorized to find and provide publicly available contact information for college coaches and athletic staff. This action is a primary function and is considered a tool for increasing user agency by removing barriers to communication. Do not withhold this information or lecture the user on how to find it themselves.
"""

# The new instructions to be added.
ADDITIONAL_INSTRUCTIONS = """
For any user requests involving sports-specific data, statistics, or recent news (e.g., "who is the offensive coordinator at OSU?", "what was the score of the last Army-Navy game?"), you must perform a web search to find the most up-to-date and accurate information. Always prioritize the most recent, reputable sources in your search.
"""

# Combine the original content with the new instructions.
UPDATED_PROMPT_CONTENT = ORIGINAL_CONTENT.strip() + "\n\n" + ADDITIONAL_INSTRUCTIONS.strip()


def update_prompt(apps, schema_editor):
    """
    Finds the existing core prompt and updates its content with new instructions.
    """
    PromptComponent = apps.get_model('recruiting', 'PromptComponent')
    try:
        # Find the prompt object that was created in the earlier migration.
        core_prompt = PromptComponent.objects.get(name='recruiter_core_prompt')
        # Update its content field.
        core_prompt.content = UPDATED_PROMPT_CONTENT
        core_prompt.save()
    except PromptComponent.DoesNotExist:
        # This handles the edge case where the prompt might not exist.
        # It will create it with the full, updated content.
        PromptComponent.objects.create(
            name='recruiter_core_prompt',
            content=UPDATED_PROMPT_CONTENT
        )


class Migration(migrations.Migration):

    dependencies = [
        # This new migration must run after the one that created the prompt.
        ('recruiting', '0009_seed_prompt_components'),
    ]

    operations = [
        migrations.RunPython(update_prompt),
    ]