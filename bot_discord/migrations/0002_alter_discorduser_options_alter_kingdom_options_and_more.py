# Generated by Django 5.1.7 on 2025-03-23 15:37

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot_discord", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="discorduser",
            options={
                "verbose_name": "Discord user",
                "verbose_name_plural": "Discord users",
            },
        ),
        migrations.AlterModelOptions(
            name="kingdom",
            options={"verbose_name": "Kingdom", "verbose_name_plural": "Kingdoms"},
        ),
        migrations.AddField(
            model_name="kingdom",
            name="lok_id",
            field=models.CharField(default="", max_length=100, unique=True),
        ),
        migrations.CreateModel(
            name="Finance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "balance",
                    models.DecimalField(
                        decimal_places=10,
                        default=0,
                        max_digits=25,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="balance",
                        to="bot_discord.discorduser",
                    ),
                ),
            ],
            options={
                "verbose_name": "Balance",
                "verbose_name_plural": "Balances",
            },
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(decimal_places=10, default=0, max_digits=21),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("SPEND", "Spend"),
                            ("RECEIVE", "Receive"),
                            ("CONTRIBUTION", "Contribution"),
                        ],
                        default="CONTRIBUTION",
                        max_length=24,
                    ),
                ),
                ("description", models.TextField(default="")),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bot_discord.discorduser",
                    ),
                ),
            ],
            options={
                "verbose_name": "Transaction",
                "verbose_name_plural": "Transactions",
                "ordering": ("owner", "-created_at"),
            },
        ),
        migrations.CreateModel(
            name="DailyContribution",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("contribution", models.DecimalField(decimal_places=10, max_digits=21)),
                ("land_id", models.PositiveIntegerField(default=100000)),
                (
                    "kingdom",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bot_discord.kingdom",
                    ),
                ),
            ],
            options={
                "verbose_name": "Daily contribution",
                "verbose_name_plural": "Daily contributions",
                "ordering": ("kingdom__name", "-date"),
                "unique_together": {("kingdom", "date")},
            },
        ),
    ]
