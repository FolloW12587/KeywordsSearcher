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
