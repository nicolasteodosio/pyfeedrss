from django.contrib import admin

# Register your models here.
from app.models import Feed, Item, UserFollowFeed, UserRelItem

admin.site.register(Feed)
admin.site.register(Item)
admin.site.register(UserRelItem)
admin.site.register(UserFollowFeed)
