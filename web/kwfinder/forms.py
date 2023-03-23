from django import forms

from . import models


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
    region = forms.ModelChoiceField(
        queryset=models.ASOWorldRegion.objects.all())
    app = forms.ModelChoiceField(
        queryset=models.App.objects.all())
