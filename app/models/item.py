from typing import Any, Optional

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

    @property
    def read(self) -> bool:
        """Property to check if the item was read

        Returns
        -------
        bool:
            A boolean if the item was read or not
        """
        from app.models.user_rel_item import UserRelItem

        return UserRelItem.read.filter(item_id=self.id).exists()

    @property
    def commented(self) -> bool:
        """Property to check if the item was commented

        Returns
        -------
        bool:
            A boolean if the item has a comment or not
        """
        from app.models.user_rel_item import UserRelItem

        return UserRelItem.commented.filter(item_id=self.id).exists()

    @property
    def comment(self) -> Optional[Any]:
        """Property to return the comment in the item

        Returns
        -------
        The comment in the item or None
        """
        if self.commented:
            from app.models.user_rel_item import UserRelItem

            return UserRelItem.commented.get(item_id=self.id).content
        return None

    @property
    def favorite(self) -> bool:
        """Property to check if the item was favorited

        Returns
        -------
        bool:
            A boolean if the item was favorited or not
        """
        from app.models.user_rel_item import UserRelItem

        return UserRelItem.favorite.filter(item_id=self.id).exists()
