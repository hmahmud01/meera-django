# Generated by Django 3.2.8 on 2024-05-26 00:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0019_productbrand_productpackprice'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='product_brand', to='backend.productbrand'),
            preserve_default=False,
        ),
    ]
