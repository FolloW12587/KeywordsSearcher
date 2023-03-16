# Generated by Django 4.1.5 on 2023-03-02 06:17

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kwfinder', '0003_app_campaign_id_app_icon_app_num'),
    ]

    operations = [
        migrations.CreateModel(
            name='KeitaroDailyAppData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='id')),
                ('date', models.DateField(verbose_name='Дата')),
                ('unique_users_count', models.PositiveIntegerField(default=0, verbose_name='Уники')),
                ('conversions_count', models.PositiveIntegerField(default=0, verbose_name='Конверсии')),
                ('sales_count', models.PositiveIntegerField(default=0, verbose_name='Продажи')),
                ('revenue', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10, verbose_name='Подтвержденный доход')),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kwfinder.app', verbose_name='Приложение')),
            ],
        ),
    ]