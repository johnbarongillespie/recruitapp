import uuid
from django.db import models
from django.contrib.auth.models import User

class PromptComponent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    content = models.TextField()

    def __str__(self):
        return self.name

class Conversation(models.Model):
    # A unique ID for each distinct conversation thread
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # A link to the user who owns this conversation
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # The text of the prompt and its response
    prompt_text = models.TextField()
    response_text = models.TextField()
    # The timestamp of when this entry was created
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"