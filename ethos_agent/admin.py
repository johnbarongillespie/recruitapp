from django.contrib import admin
from .models import PromptComponent, Conversation

admin.site.register(PromptComponent)
admin.site.register(Conversation)