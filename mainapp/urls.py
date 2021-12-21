from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginview, name='loginview'),
    path('dashboard/', views.dashboardview, name='dashboardview'),
    path('logout/', views.logoutview, name='logoutview'),
    path('clients/', views.clientlist, name='clientlist'),
    path('clients/new', views.clientnew, name='clientnew'),
    path('clients/<int:client_id>/edit', views.clientedit, name='clientedit'),
]