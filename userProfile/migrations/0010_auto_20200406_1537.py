# Generated by Django 2.2.5 on 2020-04-06 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0009_quizattempt_time_bob'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quizattempt',
            old_name='time_bob',
            new_name='time_taken',
        ),
    ]
