# Generated by Django 2.2.5 on 2020-04-25 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('navquiz', '0004_auto_20200411_2149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='navanswer',
            name='mpep_article',
            field=models.DecimalField(decimal_places=0, max_digits=5),
        ),
    ]
