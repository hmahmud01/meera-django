# Generated by Django 3.2.25 on 2024-11-23 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_shippingcharge_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]