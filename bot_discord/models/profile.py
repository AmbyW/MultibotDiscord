from django.db import models


class DiscordUser(models.Model):
    discord_id = models.CharField(max_length=255)
    discord_username = models.CharField(max_length=255)

    def __str__(self):
        return self.discord_username
