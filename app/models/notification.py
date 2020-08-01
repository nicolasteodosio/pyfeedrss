from django.contrib.auth.models import User
from django.db import models

from app.models.base import BaseModel


class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    content = models.TextField("Content")
    read = models.BooleanField("Read", default=False)

    def __str__(self):
        return self.content
