# Generated by Django 4.0.5 on 2023-02-28 18:50

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('postapp', '0006_alter_comment_like_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='like_user',
            field=models.ManyToManyField(null=True, related_name='like_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='comment',
            name='open_user',
            field=models.ManyToManyField(null=True, related_name='open_users', to=settings.AUTH_USER_MODEL),
        ),
    ]
