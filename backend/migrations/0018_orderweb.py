# Generated by Django 3.2.19 on 2024-05-25 07:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0017_orderstatus_remark'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderWeb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(blank=True, max_length=150, null=True)),
                ('phone', models.CharField(max_length=13)),
                ('address', models.CharField(max_length=200)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='backend.order')),
            ],
        ),
    ]
