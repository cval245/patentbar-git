# Generated by Django 2.2.5 on 2020-04-11 21:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0013_auto_20200411_2123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='navanswerssubmitted',
            name='answer',
        ),
        migrations.AddField(
            model_name='navanswerssubmitted',
            name='article_submitted',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='navanswerssubmitted',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='navquiz.NavQuestion'),
        ),
    ]
