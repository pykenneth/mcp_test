"""
Application configuration for the users app.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuration for the users app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'User Management'

    def ready(self):
        """
        Import signal handlers when app is ready.
        """
        import apps.users.signals  # noqa
