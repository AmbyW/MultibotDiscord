from django.db import models

from .profile import DiscordUser


class Kingdom(models.Model):
    name = models.CharField(max_length=100)
    continent = models.PositiveSmallIntegerField(default=0)
    lok_id = models.CharField(max_length=100, default="", unique=True)
    discord_profile = models.ForeignKey(DiscordUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="kingdoms")

    class Meta:
        verbose_name = 'Kingdom'
        verbose_name_plural = 'Kingdoms'

    def __str__(self):
        return f"{self.name} (C{self.continent})"
