# Generated by Django 4.0.5 on 2023-03-25 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postapp', '0012_alter_becomment_id_alter_bequestion_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]