from django.db import models
from django.db.models.deletion import CASCADE
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth.models import User

class Client(models.Model):
    name = models.CharField(max_length=40, null=False, validators=[MinLengthValidator(4)])
    owner = models.ForeignKey(User, on_delete=CASCADE)

    def __str__(self):
        return str(self.id) + " - " + self.name

class Project(models.Model):
    name = models.CharField(max_length=40, null=False, validators=[MinLengthValidator(4)])
    client = models.ForeignKey(Client, on_delete=CASCADE)
    owner = models.ForeignKey(User, on_delete=CASCADE)

    def __str__(self):
        return str(self.id) + " - " + self.name

    @property
    def clientobj(self):
        return self.client

class Task(models.Model):
    name = models.CharField(max_length=40, null=False, validators=[MinLengthValidator(4)])
    estimated_time = models.CharField(max_length=5, null=False, validators=[MinLengthValidator(5),MaxLengthValidator(5)])
    project = models.ForeignKey(Project, on_delete=CASCADE)
    owner = models.ForeignKey(User, on_delete=CASCADE)

    def __str__(self):
        return str(self.id) + " - " + self.name

    @property
    def projectobj(self):
        return self.project

class TimeEntry(models.Model):
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=False)
    duration = models.CharField(max_length=5, null=False, validators=[MinLengthValidator(5),MaxLengthValidator(5)])
    task = models.ForeignKey(Task, on_delete=CASCADE)
    owner = models.ForeignKey(User, on_delete=CASCADE)

    def __str__(self):
        return str(self.id)

    @property
    def taskobj(self):
        return self.task