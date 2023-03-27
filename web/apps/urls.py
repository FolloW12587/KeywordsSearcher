from django.urls import path

from . import views

urlpatterns = [
    path('',
         views.appsAnalytics,
         name='app_info'),
    path('<int:app_id>/',
         views.appAnalytics,
         name='app_info'),
    path('<int:app_id>/console_data/',
         views.consoleDataAdd,
         name='console_data_add'),
    path('<int:app_id>/keywords/',
         views.app_keywords,
         name='app_keywords'),
    path('<int:app_id>/keywords/add/',
         views.add_keyword_to_app,
         name='app_keywords_add'),
    path('add/',
         views.add_app,
         name='app_info_add'),
]
