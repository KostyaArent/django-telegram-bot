# Generated by Django 3.2 on 2022-06-06 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0009_auto_20220606_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilestatushistory',
            name='date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата'),
        ),
    ]