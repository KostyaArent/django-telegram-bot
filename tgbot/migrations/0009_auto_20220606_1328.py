# Generated by Django 3.2 on 2022-06-06 10:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0008_profilestatushistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='hr_comment',
            field=models.TextField(blank=True, null=True, verbose_name='Комментарий'),
        ),
        migrations.AddField(
            model_name='profilestatushistory',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='experience',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tgbot.experience', verbose_name='Опыт'),
        ),
    ]