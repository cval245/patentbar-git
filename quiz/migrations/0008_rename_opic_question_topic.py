# Generated by Django 3.2.5 on 2021-07-10 01:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0007_question_opic'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='opic',
            new_name='topic',
        ),
    ]