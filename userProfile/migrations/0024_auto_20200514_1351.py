# Generated by Django 2.2.5 on 2020-05-14 13:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_module_quiz'),
        ('userProfile', '0023_coursecompletion_modelcompletion'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleCompletion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finished_bool', models.BooleanField(default=False)),
                ('course_attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userProfile.CourseCompletion')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Module')),
            ],
        ),
        migrations.DeleteModel(
            name='ModelCompletion',
        ),
    ]
