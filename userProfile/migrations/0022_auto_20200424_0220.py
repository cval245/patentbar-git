# Generated by Django 2.2.5 on 2020-04-24 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0021_quizattempt_user_attempt_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='navanswerssubmitted',
            name='start_time',
            field=models.DateTimeField(),
        ),
    ]
