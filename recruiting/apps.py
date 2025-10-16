from django.apps import AppConfig

# Change the class name from EthosAgentConfig to RecruitingConfig
class RecruitingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recruiting'

    def ready(self):
        """
        Import signals when Django starts to ensure they're registered.
        This enables auto-updating of UserAnalytics in real-time.
        """
        import recruiting.signals  # noqa: F401