from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters

from . import models, serializers


class AppView(ReadOnlyModelViewSet):
    """ View for output list of apps. It has filters by `platform__id` field
      and it can be searched by its name. """
    queryset = models.App.objects.all()
    serializer_class = serializers.AppSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['platform__id', ]
    search_fields = ['name', ]
    ordering_fields = ['name', ]


class AppPlatformView(ReadOnlyModelViewSet):
    """ View for output list of app platforms """
    queryset = models.AppPlatform.objects.all()
    serializer_class = serializers.AppPlatformSerializer
    permission_classes = [IsAuthenticated, ]


class KeywordView(ReadOnlyModelViewSet):
    """ View for output list of keywords. It has filters 
    by `region` field and it can be searched by its name. """
    queryset = models.Keyword.objects.all()
    serializer_class = serializers.KeywordSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, ]
    filterset_fields = ['region', ]
    search_fields = ['name', ]

    def get_queryset(self):
        has_data = self.request.GET.get('has_data')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if has_data and (has_data == '1') and start_date and end_date:
            filter_ids = models.DailyAggregatedPositionData.objects.filter(
                date__lte=end_date, date__gte=start_date).exclude(position=0)

            data_app_ids = self.request.GET.get('data_app_ids')
            if data_app_ids:
                filter_ids = filter_ids.filter(
                    app__id__in=data_app_ids.split(','))

            filter_ids = filter_ids.values_list(
                'keyword', flat=True).distinct()

            self.queryset = models.Keyword.objects.filter(
                id__in=list(filter_ids))

        return super().get_queryset()


class DailyAggregatedDataView(ReadOnlyModelViewSet):
    """ View for output daily aggregated data for the given date range.
    `date__gte` should be the start of the range and `date__lte` is its end.
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


class AppPositionScriptRunDataView(ReadOnlyModelViewSet):
    queryset = models.AppPositionScriptRunData.objects.all()
    serializer_class = serializers.AppPositionScriptRunDataSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, ]
    filterset_fields = {
        'keyword__id': ['exact', ],
        'app__id': ['exact', ],
        # 'date': ['exact', 'gte', 'lte']
    }
    ordering_fields = ['run__started_at', ]

    def get_queryset(self):
        queryset = super().get_queryset()
        date = self.request.GET.get('date')
        if date:
            queryset = queryset.filter(
                run__started_at__gte=f"{date} 00:00:00", run__started_at__lte=f"{date} 23:59:59")
        return queryset


class KeitaroDailyAppDataView(ReadOnlyModelViewSet):
    queryset = models.KeitaroDailyAppData.objects.all()
    serializer_class = serializers.KeitaroDailyAppDataSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, ]
    filterset_fields = {
        'app__id': ['exact', ],
        'date': ['exact', 'gte', 'lte']
    }
    ordering_fields = ['date', ]


class ConsoleDailyDataView(ReadOnlyModelViewSet):
    queryset = models.ConsoleDailyData.objects.all()
    serializer_class = serializers.ConsoleDailyDataSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, ]
    filterset_fields = {
        'app__id': ['exact', ],
        'keyword__id': ['exact', ],
        'date': ['exact', 'gte', 'lte']
    }
    ordering_fields = ['date', ]


class ASOWorldOrderKeywordDataView(ReadOnlyModelViewSet):
    queryset = models.ASOWorldOrderKeywordData.objects.all()
    serializer_class = serializers.ASOWorldOrderKeywordDataSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, ]
    filterset_fields = {
        'order__app__id': ['exact', ],
        'keyword__id': ['exact', ],
        'date': ['exact', 'gte', 'lte']
    }
    ordering_fields = ['date', ]


@login_required
def dailyAnalytics(request):
    """ View for showing daily analytics page """
    apps = models.App.objects.all()
    return render(request, 'kwfinder/daily_stats.html', {'apps': apps})
