# Generated by Django 4.1.7 on 2023-03-14 06:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kwfinder', '0010_asoworldorder_consoledailydata_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asoworldorderkeyworddata',
            name='state',
        ),
    ]
