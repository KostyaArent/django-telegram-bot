# Generated by Django 3.2 on 2022-06-07 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0018_remove_profile_experience'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='status',
            field=models.CharField(blank=True, choices=[('0', 'Не обработано'), ('1', 'Недозвон'), ('2', 'Первичное собеседование'), ('3', 'Пробный день'), ('4', 'Итоговое собеседование'), ('5', 'Оформление'), ('6', 'Самоотказ'), ('7', 'Отказ от рекрутера'), ('8', 'Резерв'), ('9', 'Незавершенная')], default='9', max_length=300, null=True, verbose_name='Статус анкеты'),
        ),
        migrations.AlterField(
            model_name='profilestatushistory',
            name='status',
            field=models.CharField(blank=True, choices=[('0', 'Не обработано'), ('1', 'Недозвон'), ('2', 'Первичное собеседование'), ('3', 'Пробный день'), ('4', 'Итоговое собеседование'), ('5', 'Оформление'), ('6', 'Самоотказ'), ('7', 'Отказ от рекрутера'), ('8', 'Резерв'), ('9', 'Незавершенная')], max_length=300, null=True, verbose_name='Статус анкеты'),
        ),
    ]
