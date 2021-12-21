from django.db import models
from django.db.models.deletion import CASCADE
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User

class Client(models.Model):
    name = models.CharField(max_length=40, null=False, validators=[MinLengthValidator(4)])
    owner = models.ForeignKey(User, on_delete=CASCADE)

    def __str__(self):
        return str(self.id) + " - " + self.name

class Project(models.Model):
    name = models.CharField(max_length=40, null=False)
    client = models.ForeignKey(Client, on_delete=CASCADE)
    owner = models.ForeignKey(User, on_delete=CASCADE)

    def __str__(self):
        return str(self.id) + " - " + self.name

class Task(models.Model):
    name = models.CharField(max_length=40, null=False)
    project = models.ForeignKey(Project, on_delete=CASCADE)
    owner = models.ForeignKey(User, on_delete=CASCADE)

    def __str__(self):
        return str(self.id) + " - " + self.name
