# Generated by Django 4.1.7 on 2023-03-29 01:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kwfinder', '0019_alter_app_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='keitarodailyappdata',
            options={'permissions': (('can_see_keitaro_revenue', 'Видит доход в кейтаро'),), 'verbose_name': 'Данные из keitaro', 'verbose_name_plural': 'Данные из keitaro'},
        ),
    ]