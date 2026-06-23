from django.apps import AppConfig


class GamificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'poweratomic.gamification'
    label = 'gamification'

    def ready(self):
        from . import signals  # noqa: F401 - import registers the @receiver handlers