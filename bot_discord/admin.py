from django.contrib import admin

from .models import Kingdom, DiscordUser


@admin.register(Kingdom)
class KingdomAdmin(admin.ModelAdmin):
    pass


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    pass

