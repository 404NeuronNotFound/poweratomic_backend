from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'poweratomic.accounts'
    label = 'accounts'  # keeps migration table names and AUTH_USER_MODEL = 'accounts.User' short