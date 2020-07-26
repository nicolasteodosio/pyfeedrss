from django.db import models


class BaseModel(models.Model):
    """BaseModel class created to implement fields that all models will use

    """

    created_at = models.DateTimeField("Created at", auto_now_add=True)
    modified_at = models.DateTimeField("Modified at", auto_now=True)

    class Meta:
        abstract = True
