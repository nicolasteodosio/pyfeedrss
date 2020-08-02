from datetime import datetime
from time import mktime
from typing import List

from django.db import models

from app.models.base import BaseModel
from app.models.feed import Feed


class ItemManager(models.Manager):
    def bulk_entries_create(self, feed_id: int, parsed_entries: List) -> None:
        """Function responsible for bulk_creating items parsed in tasks

        Parameters
        ----------
        feed_id: int
            Feed id
        parsed_entries: List
            List of feed entries to be created
        Returns
        -------

        """
        entries_to_create = []
        for entry in parsed_entries:
            entries_to_create.append(
                Item(
                    feed_id=feed_id,
                    title=entry["title"],
                    link=entry["link"],
                    description=entry["summary"],
                    published_at=datetime.fromtimestamp(
                        mktime(entry["published_parsed"])
                    ),
                )
            )
        self.bulk_create(entries_to_create)


class Item(BaseModel):
    """Item model class

    """

    feed = models.ForeignKey(Feed, on_delete=models.DO_NOTHING)
    title = models.CharField("Title", max_length=100)
    link = models.URLField("Link")
    description = models.TextField("Description")
    published_at = models.DateTimeField("Published Date")
    objects = ItemManager()

    def __str__(self) -> str:
        return f"{self.title}"
