from django.db import models


class DiscordUser(models.Model):
    discord_id = models.CharField(max_length=255)
    discord_username = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Discord user'
        verbose_name_plural = 'Discord users'

    def __str__(self):
        return self.discord_username
