from django.db import models
from django.contrib.auth.models import User


class Tasktodo(models.Model):
    usname = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.CharField(max_length=200)
    task_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task
