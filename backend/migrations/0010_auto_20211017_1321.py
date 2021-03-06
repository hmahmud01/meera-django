# Generated by Django 3.2.7 on 2021-10-17 13:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0009_remove_product_pack_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='PackSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(blank=True, max_length=128, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='pack_size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_pack_size', to='backend.packsize'),
        ),
    ]
