from django import forms
from . import models

class ClientForm(forms.ModelForm):
    class Meta:
        model = models.Client
        fields = ['name']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ['name']

class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ['name', 'estimated_time']