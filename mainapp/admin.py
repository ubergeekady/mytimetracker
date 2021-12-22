from django.contrib import admin
from django.db import models
from . import models

@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(models.TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'durationminutes','durationseconds')