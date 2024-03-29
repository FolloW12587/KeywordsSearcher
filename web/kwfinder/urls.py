from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("apps", views.AppView, basename="apps")
router.register("app_platforms", views.AppPlatformView, basename="app_platforms")
router.register("app_groups", views.AppGroupView, basename="app_groups")
router.register("keywords", views.KeywordView, basename="keywords")
router.register("daily_data", views.DailyAggregatedDataView, basename="daily_data")
router.register("daily_data_joined", views.DailyAggregatedJoinedDataView, basename="daily_data_joined")
router.register("keitaro_data", views.KeitaroDailyAppDataView, basename="keitaro_data")
router.register("console_data", views.ConsoleDailyDataView, basename="console_data")
router.register("position_data", views.AppPositionScriptRunDataView, basename="position_data")
router.register("asoworld_data", views.ASOWorldOrderKeywordDataView, basename="asoworld_data")
# router.register('', views.AppView, basename='apps')

urlpatterns = [
    path("", views.dailyAnalytics, name="analytics"),
    path("groups_analytics/", views.groupsAnalytics, name="groups_analytics"),
    #     path('console_data_api/',
    #          views.ConsoleDataApiView.as_view(),
    #          name='console_data_api')
]
urlpatterns += router.urls
