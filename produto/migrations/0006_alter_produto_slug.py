# Generated by Django 3.2.21 on 2024-03-09 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produto', '0005_alter_produto_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]
