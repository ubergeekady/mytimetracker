from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginview, name='loginview'),
    path('dashboard/', views.dashboardview, name='dashboardview'),
    path('logout/', views.logoutview, name='logoutview'),
    path('clients/', views.clientview, name='clientview'),
]