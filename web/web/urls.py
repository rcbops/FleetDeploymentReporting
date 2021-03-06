from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'web'
urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='web/login.html'),
        name='login'
    ),
    path('logout/', auth_views.logout_then_login, name='logout'),
    path(
        'browse/details/<str:obj_model>/<str:obj_id>',
        views.index,
        name='browse'
    ),
    path('browse', views.index, name='browse'),
    path('reporting', views.index, name='reporting'),
    path('status', views.index, name='status'),
    path('', views.index, name='index')
]
