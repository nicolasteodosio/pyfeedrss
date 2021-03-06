from typing import List

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet
from django.utils.timezone import now
from djchoices import ChoiceItem, DjangoChoices

from app.models.base import BaseModel
from app.models.item import Item


class UserRelItemKind(DjangoChoices):
    """Class responsible to identify all kinds of relationships between User and Item

    """

    comment = ChoiceItem("comment", "Comment")
    read = ChoiceItem("read", "Read")
    favorite = ChoiceItem("favorite", "Favorite")
    unfavorite = ChoiceItem("unfavorite", "Unfavorite")


class UserCommentItemManager(models.Manager):
    """UserCommentItemManager to make easier to do queries for commented items

    """

    def get_queryset(self) -> QuerySet:
        """Overriding queryset to automatically get commented is

        Returns
        -------

        """
        return super().get_queryset().filter(kind=UserRelItemKind.comment)


class UserReadItemManager(models.Manager):
    """UserReadItemManager to make easier to do queries for read items

    """

    def get_queryset(self) -> QuerySet:
        """Overriding queryset to automatically get read items

        Returns
        -------

        """
        return super().get_queryset().filter(kind=UserRelItemKind.read)


class UserFavoriteItemManager(models.Manager):
    """UserFavoriteItemManager to make easier to do queries for favorite items

    """

    def get_queryset(self) -> QuerySet:
        """Overriding queryset to automatically get favorite items

        Returns
        -------

        """
        return (
            super()
            .get_queryset()
            .filter(kind=UserRelItemKind.favorite, disabled_at__isnull=True)
        )


class UserRelItemManager(models.Manager):
    def bulk_update_favorite(self, user_rel_items: List) -> None:
        """Function responsible for bulk_updating favorites
        feed to mark as disabled, so been unfavorite

        Parameters
        ----------
        user_rel_items: List

        Returns
        -------

        """
        for user_rel_item in user_rel_items:
            user_rel_item.disabled_at = now()
        self.bulk_update(user_rel_items, ["disabled_at"])


class UserRelItem(BaseModel):
    """UserRelItem model class

    """

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    kind = models.CharField("Kind", max_length=50, choices=UserRelItemKind.choices)
    content = models.TextField("Content", null=True, blank=True)
    disabled_at = models.DateTimeField("Disabled at", null=True)

    read = UserReadItemManager()
    commented = UserCommentItemManager()
    favorite = UserFavoriteItemManager()
    objects = UserRelItemManager()

    def __str__(self) -> str:
        return f"{self.kind}"
