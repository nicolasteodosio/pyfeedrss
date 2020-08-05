from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from app.forms import AddCommentForm, MarkItemForm
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
        items = Item.objects.filter(feed_id=feed.id)

        reads = UserRelItem.read.filter(item=OuterRef("pk"))
        favorites = UserRelItem.favorite.filter(item=OuterRef("pk"))
        commented = UserRelItem.commented.filter(item=OuterRef("pk"))
        comment_content = commented.values("content")

        items = items.annotate(
            read=Exists(reads),
            favorite=Exists(favorites),
            commented=Exists(commented),
            comment=comment_content,
        )

        return render(request, "list_item.html", {"items": items, "feed": feed},)
    except Feed.DoesNotExist:
        raise Http404("Feed does not exist")
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
            messages.success(request, "Comment was added to item.")
        else:
            messages.error(request, f"Form not valid: {form.errors}")
            render(request, "add_comment.html", {"form": form, "messages": form.errors})
    else:
        form = AddCommentForm()
    return render(request, "add_comment.html", {"form": form})


@login_required()
def mark_as_kind(request: HttpRequest) -> JsonResponse:
    """View to mark a item as favorite.

    Parameters
    ----------
    request: HttpRequest

    Returns
    -------

    """
    if request.is_ajax and request.method == "POST":
        form = MarkItemForm(request.POST)
        if form.is_valid():
            item_id = form.cleaned_data.get("item_id")
            kind = form.cleaned_data.get("kind")

            if kind == UserRelItemKind.unfavorite:
                favorite_rel = UserRelItem.objects.filter(
                    user_id=request.user.id,
                    item_id=item_id,
                    kind=UserRelItemKind.favorite,
                    disabled_at__isnull=True,
                )
                UserRelItem.objects.bulk_update_favorite(favorite_rel)
                return JsonResponse(
                    {"message": f"The item was marked as {kind}."}, status=200
                )
            UserRelItem.objects.create(
                user_id=request.user.id,
                item_id=item_id,
                kind=UserRelItemKind.get_choice(kind).value,
            )
            return JsonResponse(
                {"message": f"The item was marked as {kind}."}, status=200
            )
        return JsonResponse({"error": form.errors}, status=400)
    return JsonResponse({"error": "An unexpected error occurred"}, status=500)
