from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
import logging
from rest_framework import filters
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from . import models, serializers
from .authentication import TokenAuthSupportQueryString
from web.apps.permissions import get_allowed_apps


logger = logging.getLogger(__name__)


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

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.has_perm('kwfinder.can_see_all'):
            return queryset

        if not hasattr(self.request.user, 'profile'):
            return queryset.none()

        return queryset.filter(
            app__in=self.request.user.profile.apps_allowed.all())


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
        queryset = super().get_queryset()

        if not self.request.user.has_perm('kwfinder.can_see_all'):
            if not hasattr(self.request.user, 'profile'):
                queryset = queryset.none()
            else:
                queryset = queryset.filter(
                    app__in=self.request.user.profile.apps_allowed.all())

        if has_data and (has_data == '1') and start_date and end_date:
            filter_ids = models.DailyAggregatedPositionData.objects.filter(
                date__lte=end_date, date__gte=start_date).exclude(position=0)

            data_app_ids = self.request.GET.get('data_app_ids')
            if data_app_ids:
                filter_ids = filter_ids.filter(
                    app__id__in=data_app_ids.split(','))

            filter_ids = filter_ids.values_list(
                'keyword', flat=True).distinct()

            queryset = queryset.filter(
                id__in=list(filter_ids))

        return queryset


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
        'keyword__region': ['exact', ],
        'app__id': ['exact', ],
        'app__group': ['exact', ],
        'date': ['exact', 'gte', 'lte'],
    }
    ordering_fields = ['date', ]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.has_perm('kwfinder.can_see_all'):
            return queryset

        if not hasattr(self.request.user, 'profile'):
            return queryset.none()

        return queryset.filter(
            app__in=self.request.user.profile.apps_allowed.all())


class DailyAggregatedJoinedDataView(ReadOnlyModelViewSet):
    """ View for output daily aggregated data for the given date range.
    `date__gte` should be the start of the range and `date__lte` is its end.
    Also it has filters by `keyword__id` and `app__id` fields. """
    queryset = models.DailyAggregatedPositionData.objects.all()
    serializer_class = serializers.DailyAggregatedPositionJoindedDataSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, ]
    # filterset_fields = ['keyword__id', 'app__id', ]
    filterset_fields = {
        'keyword__id': ['exact', ],
        'keyword__region': ['exact', ],
        'app__id': ['exact', ],
        'app__group': ['exact', ],
        'date': ['exact', 'gte', 'lte'],
        'position': ['lte', 'gte', ]
    }
    ordering_fields = ['date', ]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.has_perm('kwfinder.can_see_all'):
            return queryset

        if not hasattr(self.request.user, 'profile'):
            return queryset.none()

        return queryset.filter(
            app__in=self.request.user.profile.apps_allowed.all())

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        sql, params = queryset.query.sql_with_params()
        raw_sql = """
        SELECT filtered_data.id,
            filtered_data.date,
            filtered_data.app_id,
            filtered_data.keyword_id,
            filtered_data.position,
            kwfinder_consoledailydata.installs,
            kwfinder_consoledailydata.views,
            aso_data.aso_installs
            from ({}) as filtered_data
                LEFT JOIN kwfinder_consoledailydata ON filtered_data.app_id = kwfinder_consoledailydata.app_id
                and filtered_data.keyword_id = kwfinder_consoledailydata.keyword_id
                and filtered_data.date = kwfinder_consoledailydata.date
                LEFT JOIN (
                    select kwfinder_asoworldorderkeyworddata.installs aso_installs,
                        kwfinder_asoworldorderkeyworddata.date,
                        kwfinder_asoworldorderkeyworddata.keyword_id,
                        kwfinder_asoworldorder.app_id
                    from kwfinder_asoworldorderkeyworddata
                        LEFT JOIN kwfinder_asoworldorder on kwfinder_asoworldorderkeyworddata.order_id = kwfinder_asoworldorder.id
                ) aso_data on filtered_data.app_id = aso_data.app_id
                and filtered_data.keyword_id = aso_data.keyword_id
                and filtered_data.date = aso_data.date
        """.format(sql)

        queryset = models.DailyAggregatedPositionData.objects.raw(
            raw_sql, params)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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

        if not self.request.user.has_perm('kwfinder.can_see_all'):
            if not hasattr(self.request.user, 'profile'):
                queryset = queryset.none()
            else:
                queryset = queryset.filter(
                    app__in=self.request.user.profile.apps_allowed.all())

        date = self.request.GET.get('date')
        if date:
            queryset = queryset.filter(
                run__started_at__gte=f"{date} 00:00:00", run__started_at__lte=f"{date} 23:59:59")
        return queryset


class KeitaroDailyAppDataView(ReadOnlyModelViewSet):
    queryset = models.KeitaroDailyAppData.objects.all()
    # serializer_class = serializers.KeitaroDailyAppDataSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, ]
    filterset_fields = {
        'app__id': ['exact', 'in'],
        'date': ['exact', 'gte', 'lte']
    }
    ordering_fields = ['date', ]

    def get_serializer_class(self):
        # type: ignore
        if self.request.user.has_perm('kwfinder.can_see_keitaro_revenue'):
            return serializers.KeitaroDailyAppDataSerializer

        return serializers.KeitaroDailyAppDataSerializerNonStaff

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.has_perm('kwfinder.can_see_all'):
            return queryset

        if not hasattr(self.request.user, 'profile'):
            return queryset.none()

        return queryset.filter(
            app__in=self.request.user.profile.apps_allowed.all())


class ConsoleDailyDataView(ReadOnlyModelViewSet):
    queryset = models.ConsoleDailyData.objects.all()
    serializer_class = serializers.ConsoleDailyDataSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, ]
    filterset_fields = {
        'app__id': ['exact', 'in'],
        'keyword__id': ['exact', 'in'],
        'date': ['exact', 'gte', 'lte']
    }
    ordering_fields = ['date', ]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.has_perm('kwfinder.can_see_all'):
            return queryset

        if not hasattr(self.request.user, 'profile'):
            return queryset.none()

        return queryset.filter(
            app__in=self.request.user.profile.apps_allowed.all())


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

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.has_perm('kwfinder.can_see_all'):
            return queryset

        if not hasattr(self.request.user, 'profile'):
            return queryset.none()

        return queryset.filter(
            order__app__in=self.request.user.profile.apps_allowed.all())


class ConsoleDataApiView(APIView):
    """ API view that recieves console data """

    authentication_classes = [
        SessionAuthentication, TokenAuthSupportQueryString, ]
    parser_classes = [JSONParser, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request) -> Response:
        serializer = serializers.ConsoleDailyAPIDataSerializer(
            data=request.data, many=True)
        logger.info(f"New console data {serializer.initial_data}.")

        if not serializer.is_valid():
            return Response({"error": "invalid data"}, status=400)

        response = {
            'updated': 0,
            'not_found': 0,
            'created': 0
        }

        for data in serializer.data:
            app = get_object_or_404(models.App, num=data['app_num'])

            keyword = app.keywords.filter(
                name=data['keyword'], region=data['region']).first()
            if not keyword:
                response['not_found'] += 1
                continue

            consoleData = models.ConsoleDailyData.objects.filter(
                app=app, keyword=keyword, date=data['date']).first()

            if not consoleData:
                models.ConsoleDailyData.objects.create(
                    app=app, keyword=keyword, date=data['date'],
                    views=data['views'], installs=data['installs'])
                response['created'] += 1
                continue

            consoleData.views = data['views']
            consoleData.installs = data['installs']
            consoleData.save()
            response['updated'] += 1

        return Response(response)


@login_required
def dailyAnalytics(request):
    """ View for showing daily analytics page """
    apps = get_allowed_apps(request)
    return render(request, 'kwfinder/daily_stats.html', {'apps': apps})


@login_required
def groupsAnalytics(request):
    """ View for showing groups analytics page """
    groups = models.AppGroup.objects.all()
    regions = models.ASOWorldRegion.objects.all()
    return render(request, 'kwfinder/groups_stats.html',
                  {'groups': groups, "regions": regions})
