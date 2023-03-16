from rest_framework import serializers

from . import models


class AppTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppType
        fields = '__all__'


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.App
        fields = '__all__'


class AppPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppPlatform
        fields = '__all__'


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Keyword
        fields = '__all__'


class DailyAggregatedPositionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DailyAggregatedPositionData
        fields = '__all__'


class AppPositionScriptRunDataSerializer(serializers.ModelSerializer):
    datetime = serializers.DateTimeField(
        source="run.started_at", format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = models.AppPositionScriptRunData
        fields = '__all__'


class KeitaroDailyAppDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.KeitaroDailyAppData
        fields = '__all__'


class ConsoleDailyDataSerializer(serializers.ModelSerializer):
    conversion = serializers.ReadOnlyField()
    
    class Meta:
        model = models.ConsoleDailyData
        fields = '__all__'


class ASOWorldOrderKeywordDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ASOWorldOrderKeywordData
        fields = '__all__'
