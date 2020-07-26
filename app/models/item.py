from django.db import models

from app.models.base import BaseModel
from app.models.feed import Feed


class Item(BaseModel):
    """Item model calss

    """

    feed = models.ForeignKey(Feed, on_delete=models.DO_NOTHING)
    title = models.CharField("Title", max_length=100)
    link = models.URLField("Link")
    description = models.TextField("Description")
    published_at = models.DateTimeField("Published Date")

    def __str__(self) -> str:
        return f"{self.title}"
