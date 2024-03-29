# Generated by Django 2.2.5 on 2019-12-29 02:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_auto_20191227_0035'),
        ('userProfile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswersSubmitted',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.IntegerField()),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Answer')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Question')),
            ],
        ),
        migrations.DeleteModel(
            name='userProfileAnswersSubmitted',
        ),
    ]
