# Generated by Django 3.2.12 on 2022-05-18 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0015_orderstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderapp',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
