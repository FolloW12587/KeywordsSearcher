from django import forms

from . import models


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
    app_type = forms.ModelChoiceField(queryset=models.AppType.objects.all())