# Generated by Django 5.0.3 on 2024-03-19 15:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pedido", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="pedido",
            name="qtd_total",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
