from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from app.models.feed import Feed
from app.models.item import Item


@login_required()
def list(request: HttpRequest, feed_id: int) -> HttpResponse:
    """

    :param request:
    :param feed_id:
    :return:
    """
    feed = Feed.objects.get(id=feed_id)
    items = Item.objects.filter(feed_id=feed_id)

    return render(request, "list_item.html", {"items": items, "feed": feed},)
