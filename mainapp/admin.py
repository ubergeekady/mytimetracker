from django.contrib import admin
from django.db import models
from . import models

@admin.register(models.Client)
class ClientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(models.Project)
class ClientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(models.Task)
class ClientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(models.TimeEntry)
class ClientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'duration')