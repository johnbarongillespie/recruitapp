from django.contrib import admin
from .models import PromptComponent, Conversation, ChatSession, Sport, PlayerProfile

admin.site.register(PromptComponent)
admin.site.register(Conversation)
admin.site.register(ChatSession)
admin.site.register(Sport)
admin.site.register(PlayerProfile)