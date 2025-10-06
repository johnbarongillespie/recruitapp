from django.contrib import admin
# Corrected the import here from PlayerProfile to SportProfile
from .models import PromptComponent, Conversation, ChatSession, Sport, SportProfile, UserProfile

admin.site.register(PromptComponent)
admin.site.register(Conversation)
admin.site.register(ChatSession)
admin.site.register(Sport)
admin.site.register(SportProfile) # Register the newly named model
admin.site.register(UserProfile) # Also register UserProfile