import uuid
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class PromptComponent(models.Model):
    # ... (this model remains the same)
    name = models.CharField(max_length=100, unique=True)
    content = models.TextField()

    def __str__(self):
        return self.name

class Conversation(models.Model):
    # ... (this model remains the same)
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt_text = models.TextField()
    response_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"