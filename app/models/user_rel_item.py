from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet
from djchoices import ChoiceItem, DjangoChoices

from app.models.base import BaseModel
from app.models.item import Item


class UserRelItemKind(DjangoChoices):
    comment = ChoiceItem("comment", "Comment")
    read = ChoiceItem("read", "Read")
    favorite = ChoiceItem("favorite", "Favorite")


class UserCommentItemManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(kind=UserRelItemKind.comment)


class UserReadItemManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(kind=UserRelItemKind.read)


class UserRelItem(BaseModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    kind = models.CharField("Kind", max_length=50, choices=UserRelItemKind.choices)
    content = models.TextField("Content", null=True, blank=True)
    read = UserReadItemManager()
    commented = UserCommentItemManager()
    objects = models.Manager()

    def __str__(self) -> str:
        return f"{self.kind}"
