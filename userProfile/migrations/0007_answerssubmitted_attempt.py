# Generated by Django 2.2.5 on 2020-03-14 16:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0006_auto_20191231_1949'),
    ]

    operations = [
        migrations.AddField(
            model_name='answerssubmitted',
            name='attempt',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='userProfile.QuizAttempt'),
            preserve_default=False,
        ),
    ]