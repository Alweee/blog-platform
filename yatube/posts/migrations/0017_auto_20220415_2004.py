# Generated by Django 2.2.16 on 2022-04-15 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0016_auto_20220415_1951'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique user',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user',), name='unique user'),
        ),
    ]