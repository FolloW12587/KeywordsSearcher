from django.urls import path

from . import views


urlpatterns = [
    path('apps/',
         views.AppView.as_view({'get': 'list'}), name='apps'),
    path('app_types/',
         views.AppTypeView.as_view({'get': 'list'}), name='app_types'),
     path('app_platforms/',
         views.AppPlatformView.as_view({'get': 'list'}), name='app_platforms'),
     path('keywords/',
         views.KeywordView.as_view({'get': 'list'}), name='keywords'),
     path('daily_data/',
         views.DailyAggregatedDataView.as_view({'get': 'list'}), name='daily_data'),
]
