from django.contrib.auth.models import User
from django.db import models

from app.models.base import BaseModel
from app.models.feed import Feed


class UserFollowFeed(BaseModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    feed = models.ForeignKey(Feed, on_delete=models.DO_NOTHING)
    disabled_at = models.DateTimeField("Disabled at", null=True)

    def __str__(self):
        return f"{self.user}: {self.feed}"
