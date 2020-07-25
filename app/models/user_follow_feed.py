from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet

from app.models.base import BaseModel
from app.models.feed import Feed


class UserUnFollowFeedManager(models.Manager):
    """UserUnFollowFeedManager to make easier to do queries for unfollowed feed

    """

    def get_queryset(self) -> QuerySet:
        """Overriding queryset to automatically get unfollowed feeds

        Returns
        -------

        """
        return super().get_queryset().filter(disabled_at__isnull=False)


class UserFollowFeedManager(models.Manager):
    """UserFollowFeedManager to make easier to do queries for followed feed

    """

    def get_queryset(self) -> QuerySet:
        """Overriding queryset to automatically get followed feeds

        Returns
        -------

        """
        return super().get_queryset().filter(disabled_at__isnull=True)


class UserFollowFeed(BaseModel):
    """UserFollowFeed class model

    """

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    feed = models.ForeignKey(Feed, on_delete=models.DO_NOTHING)
    disabled_at = models.DateTimeField("Disabled at", null=True)
    unfollowed = UserUnFollowFeedManager()
    followed = UserFollowFeedManager()
    objects = models.Manager()

    def __str__(self):
        return f"{self.user}: {self.feed}"
