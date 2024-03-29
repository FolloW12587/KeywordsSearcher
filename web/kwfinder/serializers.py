from rest_framework import serializers

from . import models


class ASOWorldRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ASOWorldRegion
        fields = "__all__"


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.App
        exclude = [
            "keywords",
        ]


class AppPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppPlatform
        fields = "__all__"


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Keyword
        fields = "__all__"


class DailyAggregatedPositionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DailyAggregatedPositionData
        fields = "__all__"


class DailyAggregatedPositionJoindedDataSerializer(serializers.ModelSerializer):
    views = serializers.IntegerField()
    installs = serializers.IntegerField()
    aso_installs = serializers.IntegerField()
    app = AppSerializer()
    keyword = KeywordSerializer()

    class Meta:
        model = models.DailyAggregatedPositionData
        fields = "__all__"


class AppPositionScriptRunDataSerializer(serializers.ModelSerializer):
    datetime = serializers.DateTimeField(source="run.started_at", format="%Y-%m-%d %H:%M:%S")  # type: ignore

    class Meta:
        model = models.AppPositionScriptRunData
        fields = "__all__"


class KeitaroDailyAppDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.KeitaroDailyAppData
        fields = "__all__"


class KeitaroDailyAppDataSerializerNonStaff(serializers.ModelSerializer):
    class Meta:
        model = models.KeitaroDailyAppData
        exclude = [
            "revenue",
        ]


class ConsoleDailyDataSerializer(serializers.ModelSerializer):
    conversion = serializers.ReadOnlyField()

    class Meta:
        model = models.ConsoleDailyData
        fields = "__all__"


class ASOWorldOrderKeywordDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ASOWorldOrderKeywordData
        fields = "__all__"


class AppGroupSerializer(serializers.ModelSerializer):
    apps = serializers.SlugRelatedField(slug_field="id", many=True, read_only=True, source="app_set")

    class Meta:
        model = models.AppGroup
        fields = "__all__"


class ConsoleDailyAPIDataSerializer(serializers.Serializer):
    app_num = serializers.CharField(max_length=255)
    keyword = serializers.CharField(max_length=255)
    region = serializers.CharField(max_length=2)
    date = serializers.DateField()
    installs = serializers.IntegerField()
    views = serializers.IntegerField()
