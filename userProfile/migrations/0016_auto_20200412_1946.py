# Generated by Django 2.2.5 on 2020-04-12 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0015_auto_20200411_2149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='navanswerssubmitted',
            name='article_submitted',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=5),
        ),
    ]
