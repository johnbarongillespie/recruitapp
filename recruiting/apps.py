from django.apps import AppConfig

# Change the class name from EthosAgentConfig to RecruitingConfig
class RecruitingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recruiting'