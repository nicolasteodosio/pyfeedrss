from django.contrib.auth.models import User
from django.db import models
from djchoices import ChoiceItem, DjangoChoices

from app.models.base import BaseModel
from app.models.feed import Feed


class UserRelItem(BaseModel):
    class UserRelItemKind(DjangoChoices):
        comment = ChoiceItem("comment", "Comment")
        read = ChoiceItem("read", "Read")

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    feed = models.ForeignKey(Feed, on_delete=models.DO_NOTHING)
    kind = models.CharField("Kind", max_length=50, choices=UserRelItemKind.choices)
    content = models.TextField("Content", null=True, blnk=True)
