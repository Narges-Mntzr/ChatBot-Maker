# Generated by Django 3.2.12 on 2023-11-25 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0006_auto_20231123_2046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bot',
            name='prompt',
            field=models.TextField(default="I'm a helpful assistant who helps users alot.", max_length=1000),
        ),
    ]
