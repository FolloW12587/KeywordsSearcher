from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path(r'login/', LoginView.as_view(template_name="accounts/login.html"), name='login'),
    path(r'logout/', LogoutView.as_view(template_name="accounts/logout.html"), name='logout'),
]
