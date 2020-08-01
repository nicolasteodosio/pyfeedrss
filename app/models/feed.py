from django.db import models

from app.models.base import BaseModel


class Feed(BaseModel):
    """Feed model class

    """

    title = models.CharField("Title", max_length=100)
    link = models.URLField("Link")
    description = models.TextField("Description", null=True, blank=True)
    ttl = models.IntegerField("TTL")
    last_build_date = models.DateTimeField("Last Build Date")

    def __str__(self) -> str:
        return f"{self.title}"
