import easy
from django.contrib import admin
from django.db.models import QuerySet
from django.http.request import HttpRequest

from app.models import Feed, Item, Notification, UserFollowFeed, UserRelItem


class FeedAdmin(admin.ModelAdmin):
    """Admin class for feed model

    """

    list_display = ("id", "title", "link", "last_build_date")


class ItemAdmin(admin.ModelAdmin):
    """Admin class for item model

    """

    list_display = ("id", "feed", "link", "published_at")


class UserRelItemAdmin(admin.ModelAdmin):
    """Admin class for userrelitem model

    """

    list_display = ("id", "item", "user", "kind", "content")

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Function necessary for changing the manager responsible for filling admin list

        Parameters
        ----------
        request

        Returns
        -------

        """
        qs = self.model.objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class UserFollowFeedAdmin(admin.ModelAdmin):
    """Admin class for userfollowfeed model

    """

    list_display = ("id", "feed", "user", "disabled", "disabled_at")

    @easy.short(desc="Disabled", order="value", bool=True)
    def disabled(self, obj):
        return bool(obj.disabled_at)


class NotificationAdmin(admin.ModelAdmin):
    """Admin class for notification model

    """

    list_display = ("id", "user", "content", "read")


admin.site.register(Feed, FeedAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(UserRelItem, UserRelItemAdmin)
admin.site.register(UserFollowFeed, UserFollowFeedAdmin)
admin.site.register(Notification, NotificationAdmin)
