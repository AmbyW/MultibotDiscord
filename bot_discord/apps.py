from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MultiDiscordBotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bot_discord"
    label = "bot_discord"
    verbose_name = _("Multi Bot Discord")

    def ready(self):
        super().ready()
        print("Multi Bot ready")
