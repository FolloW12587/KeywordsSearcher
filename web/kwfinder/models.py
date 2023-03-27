from decimal import Decimal
from django.db import models


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
    google_store_link_attributes = models.TextField(
        "Аттрибуты для поиска в гугл сторе", null=True, blank=True)

    class Meta:
        verbose_name = "Регион (ASO World)"
        verbose_name_plural = "Регионы (ASO World)"
        ordering = ['code',]

    def __str__(self):
        return f"[{self.code}] {self.name}"


# class AppType(models.Model):
#     """ Модель, описывающая тип приложения """
#     id = models.AutoField("id", primary_key=True)
#     name = models.CharField("Название", max_length=255)
#     google_store_link_attributes = models.TextField(
#         "Аттрибуты для поиска в гугл сторе")
#     apple_store_link_attributes = models.TextField(
#         "Аттрибуты для поиска в эпл сторе")
#     asoworld_region = models.ForeignKey(
#         ASOWorldRegion, on_delete=models.CASCADE, verbose_name="Регион (ASO World)")

#     class Meta:
#         verbose_name = "Тип приложения"
#         verbose_name_plural = "Типы приложений"

#     def __str__(self):
#         return self.name


class App(models.Model):
    """ Модель, описывающая приложение """
    id = models.AutoField("id", primary_key=True)
    name = models.CharField("Название", max_length=255)
    package_id = models.CharField("ID пакета", max_length=255, unique=True)
    
    platform = models.ForeignKey(
        AppPlatform, verbose_name="Платформа", on_delete=models.CASCADE)
    region = models.ForeignKey(
        ASOWorldRegion, on_delete=models.CASCADE,
        verbose_name="Регион")
    keywords = models.ManyToManyField("Keyword", verbose_name="Ключевые слова")
    
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
    region = models.ForeignKey(
        ASOWorldRegion, on_delete=models.CASCADE,
        verbose_name="Регион")

    class Meta:
        verbose_name = "Ключевое слово"
        verbose_name_plural = "Ключевые слова"

    def __str__(self):
        return f"[{self.region.code}] {self.name}"


class AppPositionScriptRun(models.Model):
    """ Модель, описывающая запуски скрипта по поиску позиций
    приложения по ключевым словам """
    id = models.AutoField("id", primary_key=True)
    started_at = models.DateTimeField("Старт", auto_now_add=True)
    ended_at = models.DateTimeField(
        "Завершился", null=True, default=None, blank=True)

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


class ConsoleDailyData(models.Model):
    """ Модель, описывающая ежедневные данные из консоли по ключевым словам по приложениям """
    id = models.AutoField("id", primary_key=True)
    date = models.DateField("Дата")
    app = models.ForeignKey(
        App, verbose_name="Приложение", on_delete=models.CASCADE)
    keyword = models.ForeignKey(
        Keyword, verbose_name="Ключевое слово", on_delete=models.CASCADE)

    views = models.PositiveSmallIntegerField("Посетители", default=0)
    installs = models.PositiveSmallIntegerField("Установки", default=0)

    @property
    def conversion(self):
        return 0.0 if self.views == 0 else round(self.installs / self.views * 100, 2)

    class Meta:
        verbose_name = "Данные из консоли"
        verbose_name_plural = "Данные из консоли"

    def __str__(self):
        return f"{self.keyword.name}_{self.app.name}_{self.date.strftime(r'%Y-%m-%d')}"


class ASOWorldOrder(models.Model):
    """ Модель, описывающая заявки в ASO World"""
    DRAFT = 0
    ACTIVE = 1
    COMPLETED = 2
    INVALID = 3
    ACCOUNTING = 4
    CANCELED = 5
    PAUSED = 6
    STATE_CHOICES = (
        (DRAFT, "Draft"),
        (ACTIVE, "Active"),
        (COMPLETED, "Completed"),
        (INVALID, "Invalid"),
        (ACCOUNTING, "Accounting"),
        (CANCELED, "Canceled"),
        (PAUSED, "Paused")
    )

    PACKAGE = "PACKAGE"
    KEYWORD = "KEYWORD"
    RATE = "RATE"
    REVIEW = "REVIEW"
    COMPOSITE = "COMPOSITE"
    LREVIEW = "LREVIEW"
    GREVIEW = "GREVIEW"
    SMART = "SMART"
    INSTALLS = "INSTALLS"
    SUBMIT_TYPE_CHOICES = (
        (PACKAGE, "Package (Direct) Installs"),
        (KEYWORD, "Keyword Installs"),
        (RATE, "Ratings"),
        (REVIEW, "Reviews"),
        (COMPOSITE, "Advanced Campaign"),
        (LREVIEW, "App Review Likes Service"),
        (GREVIEW, "Guaranteed Reviews Service"),
        (SMART, "Smart Campaign"),
        (INSTALLS, "Combo Package")
    )

    SPREAD = "24h"
    ONCE = "once"
    INSTALL_TYPE_CHOICES = (
        (SPREAD, "Spread Installs Within 24h"),
        (ONCE, "All Installs At Once")
    )

    id = models.AutoField("id", primary_key=True)
    asoworld_id = models.CharField("ASO World id", max_length=255, unique=True)
    state = models.PositiveSmallIntegerField("Статус", choices=STATE_CHOICES)
    app = models.ForeignKey(
        App, verbose_name="Приложение", on_delete=models.CASCADE)
    submit_type = models.CharField(
        "Тип", choices=SUBMIT_TYPE_CHOICES, max_length=9)
    install_type = models.CharField(
        "Тип установки", choices=INSTALL_TYPE_CHOICES, max_length=4)

    price = models.DecimalField(
        "Сумма заказа", default=Decimal(0), decimal_places=2, max_digits=10)

    created_at = models.DateTimeField(
        "Создана", editable=False)
    started_at = models.DateTimeField(
        "Запущена", editable=False)
    canceled_at = models.DateTimeField(
        "Отменена", null=True, blank=True, default=None, editable=False)
    finished_at = models.DateTimeField(
        "Закончена", null=True, blank=True, default=None, editable=False)
    last_paused_at = models.DateTimeField(
        "Последняя пауза", null=True, blank=True, default=None, editable=False)

    class Meta:
        verbose_name = "Заявка ASO World"
        verbose_name_plural = "Заявки ASO World"

    def __str__(self):
        return f"[{self.asoworld_id}] {self.app.name}"


class ASOWorldOrderKeywordData(models.Model):
    """ Модель, описывающая установки по ключам для заявки в ASO World"""
    id = models.AutoField("id", primary_key=True)
    order = models.ForeignKey(
        ASOWorldOrder, on_delete=models.CASCADE, verbose_name="Заявка")
    keyword = models.ForeignKey(
        Keyword, on_delete=models.CASCADE, verbose_name="Ключевое слово")
    installs = models.PositiveSmallIntegerField("Установки", default=0)
    date = models.DateField("Дата")

    class Meta:
        verbose_name = "Установка по ключу в ASO World"
        verbose_name_plural = "Установки по ключу в ASO World"

    def __str__(self):
        return f"[{self.order.asoworld_id}] {self.keyword.name}"
