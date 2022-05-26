from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from . import models, serializers


class AppTypeView(ReadOnlyModelViewSet):
    """ View for output list of app types """
    queryset = models.AppType.objects.all()
    serializer_class = serializers.AppTypeSerializer
    permission_classes = [IsAuthenticated, ]


class AppView(ReadOnlyModelViewSet):
    """ View for output list of apps. It has filters by `app_type__id` 
    and `platform__id` fields and it can be searched by its name. """
    queryset = models.App.objects.all()
    serializer_class = serializers.AppSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['app_type__id', 'platform__id', ]
    search_fields = ['name', ]
    ordering_fields = ['name', ]


class AppPlatformView(ReadOnlyModelViewSet):
    """ View for output list of app platforms """
    queryset = models.AppPlatform.objects.all()
    serializer_class = serializers.AppPlatformSerializer
    permission_classes = [IsAuthenticated, ]


class KeywordView(ReadOnlyModelViewSet):
    """ View for output list of keywords. It has filters 
    by `app_type__id` field and it can be searched by its name. """
    queryset = models.Keyword.objects.all()
    serializer_class = serializers.KeywordSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, ]
    filterset_fields = ['app_type__id', ]
    search_fields = ['name', ]


class DailyAggregatedDataView(ReadOnlyModelViewSet):
    """ View for output daily aggregated data for the given date range.
    `start_date` should be the start of the range and `end_date` is its end.
    Also it has filters by `keyword__id` and `app__id` fields. """
    queryset = models.DailyAggregatedPositionData.objects.all()
    serializer_class = serializers.DailyAggregatedPositionDataSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, ]
    # filterset_fields = ['keyword__id', 'app__id', ]
    filterset_fields = {
        'keyword__id': ['exact', ],
        'app__id': ['exact', ],
        'date': ['exact', 'gte', 'lte']
    }
    ordering_fields = ['date', ]


def dailyAnalytics(request):
    """ View for showing daily analytics page """
    return render(request, 'kwfinder/daily_stats.html')
