from django.db import models
from django.db.models.deletion import CASCADE
from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator 
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
    durationhours = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(500)])
    durationminutes = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(60)])
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
    durationminutes = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(60)])
    durationseconds = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(60)])
    task = models.ForeignKey(Task, on_delete=CASCADE)
    owner = models.ForeignKey(User, on_delete=CASCADE)

    def __str__(self):
        return str(self.id)

    @property
    def taskobj(self):
        return self.task