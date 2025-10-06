import uuid
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    high_school = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    email_verified = models.BooleanField(default=False)
    onboarding_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class PromptComponent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Lowest numbers are assembled first.")

    def __str__(self):
        return f"{self.name} (Order: {self.order})"

class Sport(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SportProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sport_profiles')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    height = models.CharField(max_length=10, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    highlight_reel_url = models.URLField(max_length=250, blank=True)
    metrics = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.sport.name} ({self.position or 'N/A'})"

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200, default='New Chat')
    summary = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"'{self.title}' for {self.user.username} (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"

class Conversation(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True) 
    prompt_text = models.TextField()
    response_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_name = self.user.username if self.user else "Unknown User"
        if self.session:
            return f"Message from {user_name} in session {self.session.id} at {self.timestamp.strftime('%H:%M')}"
        return f"Message from {user_name} at {self.timestamp.strftime('%H:%M')}"

    class Meta:
        indexes = [
            models.Index(fields=['session', 'timestamp']),
        ]