# Generated by Django 3.2.7 on 2022-04-22 11:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='_social_user_following_+', to=settings.AUTH_USER_MODEL),
        ),
    ]