# Generated by Django 2.2.5 on 2020-05-21 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_module_quiz'),
        ('userProfile', '0024_auto_20200514_1351'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='modulecompletion',
            unique_together={('course_attempt', 'module', 'finished_bool')},
        ),
    ]
