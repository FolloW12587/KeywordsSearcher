from decimal import Decimal
from django.db import models
import uuid

# Create your models here.


class AppPlatform(models.Model):
    """ Модель, описывающая платформу приложения """
    id = models.AutoField("id", primary_key=True)
    name = models.CharField("Название", max_length=255)
    base_store_link = models.TextField(
        "Базовая ссылка на страницу поиска стора")
    asoworld_id = models.PositiveSmallIntegerField("ID в asoworld", default=1)

    class Meta:
        verbose_name = "Платформа приложения"
        verbose_name_plural = "Платформы приложений"

    def __str__(self):
        return self.name


class ASOWorldRegion(models.Model):
    """ Модель, описывающая регионы из ASO World """
    code = models.CharField("Код", max_length=2, primary_key=True, unique=True)
    name = models.CharField("Наименование", max_length=255)
    is_app_store_supported = models.BooleanField("Поддерживается в App Store")
    is_google_play_supported = models.BooleanField(
        "Поддерживается в Google Play")

    class Meta:
        verbose_name = "Регион (ASO World)"
        verbose_name_plural = "Регионы (ASO World)"

    def __str__(self):
        return f"[{self.code}] {self.name}"


class AppType(models.Model):
    """ Модель, описывающая тип приложения """
    id = models.AutoField("id", primary_key=True)
    name = models.CharField("Название", max_length=255)
    google_store_link_attributes = models.TextField(
        "Аттрибуты для поиска в гугл сторе")
    apple_store_link_attributes = models.TextField(
        "Аттрибуты для поиска в эпл сторе")
    asoworld_region = models.ForeignKey(
        ASOWorldRegion, on_delete=models.CASCADE, verbose_name="Регион (ASO World)")

    class Meta:
        verbose_name = "Тип приложения"
        verbose_name_plural = "Типы приложений"

    def __str__(self):
        return self.name


class App(models.Model):
    """ Модель, описывающая приложение """
    id = models.AutoField("id", primary_key=True)
    name = models.CharField("Название", max_length=255)
    # link = models.TextField("Ссылка в сторе")
    package_id = models.CharField("ID пакета", max_length=255, unique=True)
    platform = models.ForeignKey(
        AppPlatform, verbose_name="Платформа", on_delete=models.CASCADE)
    app_type = models.ForeignKey(
        AppType, verbose_name="Тип", on_delete=models.CASCADE)
    is_active = models.BooleanField("Активно", default=True, blank=True)
    icon = models.ImageField(
        "Иконка", upload_to="app_icons/", null=True, blank=True)

    num = models.CharField("Номер", max_length=255, unique=True)
    campaign_id = models.CharField(
        "ID кампании в keitaro", max_length=255, unique=True)

    @property
    def link(self):
        return f"https://play.google.com/store/apps/details?id={self.package_id}"

    class Meta:
        verbose_name = "Приложение"
        verbose_name_plural = "Приложения"

    def __str__(self):
        return self.name


class Keyword(models.Model):
    """ Модель, описывабщая ключевое слово """
    id = models.AutoField("id", primary_key=True)
    name = models.CharField("Название", max_length=255)
    app_type = models.ForeignKey(
        AppType, verbose_name="Тип", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Ключевое слово"
        verbose_name_plural = "Ключевые слова"

    def __str__(self):
        return self.name


class AppPositionScriptRun(models.Model):
    """ Модель, описывающая запуски скрипта по поиску позиций
    приложения по ключевым словам """
    id = models.AutoField("id", primary_key=True)
    started_at = models.DateTimeField("Старт", auto_now_add=True)
    ended_at = models.DateTimeField(
        "Завершился", null=True, default=None, blank=True)
    app_type = models.ForeignKey(
        AppType, verbose_name="Тип", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Запуск скрипта (поиск позиций приложений)"
        verbose_name_plural = "Запуски скрипта"

    def __str__(self):
        return f"[{self.id}] {self.started_at.strftime(r'%d-%m-%Y %H:%M:%S')}"


class AppPositionScriptRunData(models.Model):
    """ Модель, описывающая полученные данные в конкретный запуск скрипта
    по поиску позиций приложения по ключевым словам """
    id = models.AutoField("id", primary_key=True)
    run = models.ForeignKey(AppPositionScriptRun,
                            verbose_name="Запуск скрипта",
                            on_delete=models.CASCADE)
    keyword = models.ForeignKey(
        Keyword, verbose_name="Ключевое слово", on_delete=models.CASCADE)
    app = models.ForeignKey(
        App, verbose_name="Приложение", on_delete=models.CASCADE)
    position = models.IntegerField("Позиция", default=0)

    class Meta:
        verbose_name = "Данные запуска скрипта"
        verbose_name_plural = "Данные запуска скрипта"

    def __str__(self):
        return f"{self.keyword.name} - {self.app.name} - {self.position}"


class DailyAggregatedPositionData(models.Model):
    """ Модель, описывающая агрегированные данные 
    по позициям приложений по дням """
    id = models.AutoField("id", primary_key=True)
    date = models.DateField("Дата")
    keyword = models.ForeignKey(
        Keyword, verbose_name="Ключевое слово", on_delete=models.CASCADE)
    app = models.ForeignKey(
        App, verbose_name="Приложение", on_delete=models.CASCADE)
    position = models.IntegerField("Позиция", default=0)

    class Meta:
        verbose_name = "Агрегированные данные по дням"
        verbose_name_plural = "Агрегированные данные по дням"

    def __str__(self):
        return f"{self.keyword.name} - {self.app.name} - {self.position}"


class KeitaroDailyAppData(models.Model):
    """ Модель, описывающая данные из кейтаро по приложениям, агрегированные по дням """
    id = models.AutoField("id", primary_key=True)
    date = models.DateField("Дата")
    app = models.ForeignKey(
        App, verbose_name="Приложение", on_delete=models.CASCADE)

    UNIQUE_USERS_COUNT_FIELD_NAME = "campaign_unique_clicks"
    CONVERSIONS_COUNT_FIELD_NAME = "conversions"
    SALES_COUNT_FIELD_NAME = "sales"
    REVENUE_FIELD_NAME = "sale_revenue"
    CAMPAIGN_ID_FIELD_NAME = "campaign_id"
    DATE_FIELD_NAME = "day"

    unique_users_count = models.PositiveIntegerField("Уники", default=0)
    conversions_count = models.PositiveIntegerField("Конверсии", default=0)
    sales_count = models.PositiveIntegerField("Продажи", default=0)
    revenue = models.DecimalField(
        "Подтвержденный доход", max_digits=10, decimal_places=2, default=Decimal(0))

    class Meta:
        verbose_name = "Данные из keitaro"
        verbose_name_plural = "Данные из keitaro"

    def __str__(self):
        return f"{self.app.name}_{self.date.strftime(r'%Y-%m-%d')}"
