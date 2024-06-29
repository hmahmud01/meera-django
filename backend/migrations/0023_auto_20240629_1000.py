# Generated by Django 3.2.8 on 2024-06-29 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0022_auto_20240628_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderweb',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='orderweb',
            name='payment_status',
            field=models.CharField(blank=True, default='NOT PAID', max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='orderweb',
            name='status',
            field=models.CharField(blank=True, default='MADE', max_length=128, null=True),
        ),
    ]
