from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    modified_at = models.DateTimeField("Modified at", auto_now_add=True)

    class Meta:
        abstract = True
