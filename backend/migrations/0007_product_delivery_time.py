# Generated by Django 3.2.25 on 2025-03-23 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_product_variety'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='delivery_time',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]
