# Generated by Django 3.2 on 2022-05-25 07:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tgbot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Arcgis',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('location', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='tgbot.location')),
                ('match_addr', models.CharField(max_length=200)),
                ('long_label', models.CharField(max_length=200)),
                ('short_label', models.CharField(max_length=128)),
                ('addr_type', models.CharField(max_length=128)),
                ('location_type', models.CharField(max_length=64)),
                ('place_name', models.CharField(max_length=128)),
                ('add_num', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=128)),
                ('block', models.CharField(max_length=128)),
                ('sector', models.CharField(max_length=128)),
                ('neighborhood', models.CharField(max_length=128)),
                ('district', models.CharField(max_length=128)),
                ('city', models.CharField(max_length=64)),
                ('metro_area', models.CharField(max_length=64)),
                ('subregion', models.CharField(max_length=64)),
                ('region', models.CharField(max_length=128)),
                ('territory', models.CharField(max_length=128)),
                ('postal', models.CharField(max_length=128)),
                ('postal_ext', models.CharField(max_length=128)),
                ('country_code', models.CharField(max_length=32)),
                ('lng', models.DecimalField(decimal_places=18, max_digits=21)),
                ('lat', models.DecimalField(decimal_places=18, max_digits=21)),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
    ]
