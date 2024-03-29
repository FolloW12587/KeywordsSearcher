# Generated by Django 4.1.5 on 2023-03-03 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kwfinder', '0007_auto_20230303_0253'),
    ]

    operations = [
        migrations.CreateModel(
            name='ASOWorldRegion',
            fields=[
                ('code', models.CharField(max_length=2, primary_key=True, serialize=False, unique=True, verbose_name='Код')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('is_app_store_supported', models.BooleanField(verbose_name='Поддерживается в App Store')),
                ('is_google_play_supported', models.BooleanField(verbose_name='Поддерживается в Google Play')),
            ],
            options={
                'verbose_name': 'Регион (ASO World)',
                'verbose_name_plural': 'Регионы (ASO World)',
            },
        ),
        migrations.AddField(
            model_name='appplatform',
            name='asoworld_id',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='ID в asoworld'),
        ),
    ]
