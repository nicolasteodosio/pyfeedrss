from django.db import models

from app.models.base import BaseModel
from app.models.feed import Feed


class Item(BaseModel):
    feed = models.ForeignKey(Feed, on_delete=models.DO_NOTHING)
    title = models.CharField("Title", max_length=100)
    link = models.URLField("Link")
    description = models.TextField("Description")
    published_at = models.DateTimeField("Published Date")

    def __str__(self) -> str:
        return f"{self.title}"

    @property
    def read(self):
        """

        :return:
        """
        from app.models.user_rel_item import UserRelItem

        return UserRelItem.read.filter(item_id=self.id).exists()

    @property
    def commented(self):
        """

        :return:
        """
        from app.models.user_rel_item import UserRelItem

        return UserRelItem.commented.filter(item_id=self.id).exists()

    @property
    def comment(self):
        """

        :return:
        """
        if self.commented:
            from app.models.user_rel_item import UserRelItem

            return UserRelItem.commented.get(item_id=self.id).content
        return None

    @property
    def favorite(self):
        """

        :return:
        """
        from app.models.user_rel_item import UserRelItem

        return UserRelItem.favorite.filter(item_id=self.id).exists()
