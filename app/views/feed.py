from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.db.models.aggregates import Count
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from app.forms import AddFeedForm, UpdateFeedForm
from app.models.feed import Feed
from app.models.user_rel_item import UserRelItemKind
from app.tasks import parse_feed, update_feed


@login_required()
def add(request: HttpRequest) -> HttpResponse:
    """View for adding new feed for a user.
    Use AddFeedForm, with `url` and `alias` parameters, and `alias` being optional.
    if is valid, send a message to a dramatiq.actor task called `parse_feed`

    Parameters
    ----------
    request: HttpRequest

    Returns
    -------

    """

    if request.method == "POST":
        form = AddFeedForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get("url")
            alias = form.cleaned_data.get("alias")
            parse_feed.send(url, alias, request.user.id)
        else:
            return render(
                request, "add_feed.html", {"form": form, "messages": form.errors}
            )
    else:
        form = AddFeedForm()
    return render(request, "add_feed.html", {"form": form})


@login_required()
def list(request: HttpRequest) -> HttpResponse:
    """View for listings all feeds from a user.

    Parameters
    ----------
    request: HttpRequest

    Returns
    -------
    render list_feed.html with the followed and unfollowed feeds from a user
    """

    users_feed = Feed.objects.filter(userfollowfeed__user_id=request.user.id)
    feeds_followed = users_feed.filter(userfollowfeed__disabled_at__isnull=True)
    feeds_unfollowed = users_feed.filter(userfollowfeed__disabled_at__isnull=False)
    feeds_followed = feeds_followed.annotate(
        read_count=Count(
            "item__userrelitem__id",
            filter=Q(item__userrelitem__kind=UserRelItemKind.read),
        ),
        total=Count("item__id", distinct=True),
        unread_count=F("total") - F("read_count"),
    )
    return render(
        request,
        "list_feed.html",
        {"feeds_followed": feeds_followed, "feeds_unfollowed": feeds_unfollowed},
    )


@login_required()
def update(request: HttpRequest) -> JsonResponse:
    """View to update a feed chosen by the user.
    Receive `feedId` as a parameter and call a `dramatiq.actor` task `update_feed`

    Parameters
    ----------
    request: HttpRequest

    Returns
    -------
    JsonResponse
    """
    if request.is_ajax and request.method == "POST":
        form = UpdateFeedForm(request.POST)
        if form.is_valid():
            feed_id = form.cleaned_data.get("feed_id")
            update_feed.send(feed_id)
            return JsonResponse({"message": "The feed was sent to update."}, status=200)
        return JsonResponse({"error": form.errors}, status=400)
    return JsonResponse({"error": "An unexpected error occurred"}, status=500)
