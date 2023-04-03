from django.urls import path

from . import views

urlpatterns = [
    path('',
         views.appsAnalytics,
         name='apps_info'),
    path('<int:app_id>/',
         views.appAnalytics,
         name='apps_info'),
    path('<int:app_id>/console_data/',
         views.consoleDataAdd,
         name='console_data_add'),
    path('<int:app_id>/keywords/',
         views.app_keywords,
         name='app_keywords'),
    path('<int:app_id>/keywords/add/',
         views.add_keyword_to_app,
         name='app_keywords_add'),
    path('<int:app_id>/keywords/analytics/',
         views.app_keywords_analytics,
         name='app_keywords_analytics'),
    path('<int:app_id>/keywords/<int:keyword_id>/remove/',
         views.remove_keyword_from_app,
         name='app_keywords_remove'),
    path('add/',
         views.add_app,
         name='apps_info_add'),
]
