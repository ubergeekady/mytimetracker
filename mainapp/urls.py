from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginview, name='loginview'),
    path('dashboard/', views.dashboardview, name='dashboardview'),
    path('logout/', views.logoutview, name='logoutview'),
    path('clients/', views.clientlist, name='clientlist'),
    path('clients/new', views.clientnew, name='clientnew'),
    path('clients/<int:client_id>/edit', views.clientedit, name='clientedit'),
    path('clients/<int:client_id>/delete', views.clientdelete, name='clientdelete'),
    path('projects/<int:client_id>/', views.projectlist, name='projectlist'),
    path('projects/new/<int:client_id>/', views.projectnew, name='projectnew'),
    path('projects/<int:project_id>/edit', views.projectedit, name='projectedit'),
    path('projects/<int:project_id>/delete', views.projectdelete, name='projectdelete'),
    path('tasks/<int:project_id>/', views.tasklist, name='tasklist'),
    path('tasks/new/<int:project_id>/', views.tasknew, name='tasknew'),
    path('tasks/<int:task_id>/edit', views.taskedit, name='taskedit'),
    path('tasks/<int:task_id>/delete', views.taskdelete, name='taskdelete'),
    path('tasks/<int:task_id>/detail', views.taskdetail, name='taskdetail'),
    path('timeentry/<int:task_id>/', views.timeentry, name='timeentry'),
    path('timeentry/new/', views.newtimeentry, name='newtimeentry'),
    path('timeentry/<int:timeentry_id>/delete', views.timeentrydelete, name='timeentrydelete'),
]