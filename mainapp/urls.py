from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginview, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logoutview, name='logout'),
]