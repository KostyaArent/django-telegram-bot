# Generated by Django 3.2.13 on 2022-04-25 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0003_rm_unused_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20, unique=True, verbose_name='Title of the game')),
            ],
            options={
                'verbose_name': 'Game',
                'verbose_name_plural': 'Games',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='tgbot.user')),
                ('steam_nickname', models.TextField(blank=True, verbose_name='Steam nickname')),
                ('in_search', models.BooleanField(default=False, verbose_name='In search')),
                ('game', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='tgbot.game', verbose_name='Main game')),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
        ),
    ]