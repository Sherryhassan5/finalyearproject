# Generated by Django 5.0.6 on 2024-05-15 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_review_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, default='sherry', null=True),
        ),
    ]
