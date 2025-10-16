# recruiting/migrations/0015_userprofile_has_seen_welcome.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiting', '0014_guardrails_and_axiomism_prompt'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='has_seen_welcome',
            field=models.BooleanField(default=False),
        ),
    ]
