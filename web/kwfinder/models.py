from django.db import models

# Create your models here.


class AppPlatform(models.Model):
    """ Модель, описывающая платформу приложения """
    id = models.AutoField("id", primary_key=True)
    name = models.CharField("Название", max_length=255)
    base_store_link = models.TextField(
        "Базовая ссылка на страницу поиска стора")

    class Meta:
        verbose_name = "Платформа приложения"
        verbose_name_plural = "Платформы приложений"

    def __str__(self):
        return self.name


class AppType(models.Model):
    """ Модель, описывающая тип приложения """
    id = models.AutoField("id", primary_key=True)
    name = models.CharField("Название", max_length=255)
    google_store_link_attributes = models.TextField(
        "Аттрибуты для поиска в гугл сторе")
    apple_store_link_attributes = models.TextField(
        "Аттрибуты для поиска в эпл сторе")

    class Meta:
        verbose_name = "Тип приложения"
        verbose_name_plural = "Типы приложений"

    def __str__(self):
        return self.name


class App(models.Model):
    """ Модель, описывающая приложение """
    id = models.AutoField("id", primary_key=True)
    name = models.CharField("Название", max_length=255)
    link = models.TextField("Ссылка в сторе")
    platform = models.ForeignKey(
        AppPlatform, verbose_name="Платформа", on_delete=models.CASCADE)
    app_type = models.ForeignKey(
        AppType, verbose_name="Тип", on_delete=models.CASCADE)
    is_active = models.BooleanField("Активно", default=True, blank=True)

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
