from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from app.forms import AddCommentForm
from app.models import UserRelItem
from app.models.feed import Feed
from app.models.item import Item
from app.models.user_rel_item import UserRelItemKind


@login_required()
def list(request: HttpRequest, feed_id: int) -> HttpResponse:
    """View to list all items from a feed.

    Parameters
    ----------
    request: HttpRequest
    feed_id: int

    Returns
    -------

    """
    try:
        feed = Feed.objects.get(id=feed_id)
        items = Item.objects.filter(feed_id=feed_id)

        return render(request, "list_item.html", {"items": items, "feed": feed},)
    except Exception as e:
        raise e


@login_required()
def add_comment(request: HttpRequest, item_id: int) -> HttpResponse:
    """View to add a private commentary for a item.

    Parameters
    ----------
    request: HttpRequest
    item_id: int

    Returns
    -------

    """
    if request.method == "POST":
        form = AddCommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data.get("comment")
            UserRelItem.objects.create(
                user_id=request.user.id,
                item_id=item_id,
                content=comment,
                kind=UserRelItemKind.comment,
            )
        else:
            render(request, "add_comment.html", {"form": form, "messages": form.errors})
    else:
        form = AddCommentForm()
    return render(request, "add_comment.html", {"form": form})


@login_required()
def mark_as_read(request: HttpRequest) -> JsonResponse:
    """View to mark a item as read.

    Parameters
    ----------
    request: HttpRequest

    Returns
    -------

    """
    data = {}
    try:
        item_id = request.GET.get("itemId")
        UserRelItem.objects.create(
            user_id=request.user.id, item_id=item_id, kind=UserRelItemKind.read
        )
        data["sucess"] = "Item marked as read."
        return JsonResponse(data)
    except Exception as e:
        raise e


@login_required()
def mark_as_favorite(request: HttpRequest) -> JsonResponse:
    """View to mark a item as favorite.

    Parameters
    ----------
    request: HttpRequest

    Returns
    -------

    """
    data = {}
    try:
        item_id = request.GET.get("itemId")
        UserRelItem.objects.create(
            user_id=request.user.id, item_id=item_id, kind=UserRelItemKind.favorite
        )
        data["sucess"] = "Item marked as favorite."
        return JsonResponse(data)
    except Exception as e:
        raise e
