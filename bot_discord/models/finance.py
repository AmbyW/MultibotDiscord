from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from ..exceptions import NotEnoughBalanceException
from .kingdoms import Kingdom
from .profile import DiscordUser


class TransactionType(models.TextChoices):
    SPEND = ("SPEND", "Spend")
    RECEIVE = ("RECEIVE", "Receive")
    CONTRIBUTION = ("CONTRIBUTION", "Contribution")


class DailyContribution(models.Model):
    date = models.DateField()
    contribution = models.DecimalField(max_digits=21, decimal_places=10)
    kingdom = models.ForeignKey(Kingdom, models.CASCADE)
    land_id = models.PositiveIntegerField(default=100000)

    class Meta:
        verbose_name = "Daily contribution"
        verbose_name_plural = "Daily contributions"
        unique_together = ("kingdom", "date")
        ordering = ("kingdom__name", "-date")

    def __str__(self):
        return f"{self.kingdom}({self.date}): {self.contribution: <10.2f}"


class Transaction(models.Model):
    amount = models.DecimalField(max_digits=21, decimal_places=10, default=0)
    owner = models.ForeignKey(DiscordUser, models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(choices=TransactionType.choices, max_length=24, default=TransactionType.CONTRIBUTION)
    description = models.TextField(default="")

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ("owner", "-created_at",)

    def __str__(self):
        return f"TRX of {self.owner} ({self.amount: <10.2f})"


class Finance(models.Model):
    profile = models.ForeignKey(DiscordUser, models.CASCADE, related_name="balance")
    balance = models.DecimalField(max_digits=25, decimal_places=10, default=0, validators=[MinValueValidator(0)])
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Balance"
        verbose_name_plural = "Balances"

    def __str__(self):
        return f"{self.profile} ({self.balance: <10.2f})"


@receiver(post_save, sender=DailyContribution)
def create_trx_per_daily_contribution(_, instance, created, **kwargs):
    if created:
        kingdom = Kingdom.objects.get(id=instance.kingdom_id)
        Transaction.objects.create(
            owner_id=kingdom.discord_profile_id,
            amount=instance.contribution,
            description=f"land development contribution from kingdom {kingdom}({instance.date}): {instance.contribution} dev points"
        )


@receiver(pre_save, sender=Transaction)
def check_spend_availability(_, instance, **kwargs):
    if instance.type == TransactionType.SPEND:
        if (balance := Finance.objects.get(owner=instance.profile)) and balance.balance - instance.amount < 0:
            raise NotEnoughBalanceException()
