from django.db import models

from app.models.base import BaseModel


class Feed(BaseModel):
    title = models.CharField("Title", max_length=100)
    link = models.URLField("Link")
    description = models.TextField("Description")
    ttl = models.IntegerField("TTL")
    last_build_date = models.DateTimeField("Last Build Date")

    def __str__(self) -> str:
        return f"{self.title}"

    @property
    def unread_count(self):
        from app.models import Item

        feed_items = Item.objects.filter(feed_id=self.id)
        feed_items_count = feed_items.count()
        feed_items_read_count = 0
        for feed_item in feed_items:
            if feed_item.read:
                feed_items_read_count += 1
        return feed_items_count - feed_items_read_count
