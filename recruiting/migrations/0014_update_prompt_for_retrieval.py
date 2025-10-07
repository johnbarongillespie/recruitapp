# recruiting/migrations/0014_update_prompt_for_retrieval.py

from django.db import migrations

# This new directive will be placed at the very top of the prompt.
PRIME_DIRECTIVE = """
PRIME DIRECTIVE: When a user asks for a specific piece of factual data (e.g., a team roster, schedule, or a coach's title), your first and most important job is to perform a web search and present the most recent, official information you can find. Display this factual data clearly and directly. Only after you have provided the direct answer should you offer any of your own strategic analysis, projections, or advice. If your search cannot find an official answer, state that you could not find the information on the official team sources, and then proceed with a projection or analysis.
"""

def update_prompt(apps, schema_editor):
    """
    Finds the existing core prompt and prepends the new Prime Directive.
    """
    PromptComponent = apps.get_model('recruiting', 'PromptComponent')
    try:
        core_prompt = PromptComponent.objects.get(name='recruiter_core_prompt')
        
        # Prepend the new directive to the existing content for top priority
        updated_content = PRIME_DIRECTIVE.strip() + "\n\n" + core_prompt.content
        
        core_prompt.content = updated_content
        core_prompt.save()
    except PromptComponent.DoesNotExist:
        # This is a fallback and should not happen in a normal migration flow
        pass


class Migration(migrations.Migration):

    dependencies = [
        # This migration must run after the one we are modifying.
        ('recruiting', '0012_update_core_prompt_for_search'), 
    ]

    operations = [
        migrations.RunPython(update_prompt),
    ]