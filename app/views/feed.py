from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.db.models.aggregates import Count
from django.dispatch import Signal, receiver
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from app.forms import AddFeedForm, FeedForm
from app.models import Notification, UserFollowFeed
from app.models.feed import Feed
from app.models.user_rel_item import UserRelItemKind
from app.tasks import parse_feed, update_feed

notification_read_signal = Signal(providing_args=["notifications"])


@receiver(notification_read_signal)
def mark_notification_as_read_receiver(sender, **kwargs):
    for notification in kwargs["notifications"]:
        notification.read = True
    Notification.objects.bulk_update(kwargs["notifications"], ["read"])


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
            messages.success(request, "Feed added and sent to be parsed.")
            return redirect("list_feed")
        else:
            messages.error(request, f"Form not valid: {form.errors}")
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

    user_id = request.user.id
    users_feed = Feed.objects.filter(userfollowfeed__user_id=user_id)
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
    notifications = Notification.objects.filter(user_id=user_id, read=False)
    to_notify = []
    for notification in notifications:
        to_notify.append(notification.content)
    if to_notify:
        messages.warning(request, ",".join(to_notify))
        notification_read_signal.send(sender=Notification, notifications=notifications)
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
        form = FeedForm(request.POST)
        if form.is_valid():
            feed_id = form.cleaned_data.get("feed_id")
            update_feed.send(feed_id, request.user.id)
            return JsonResponse({"message": "The feed was sent to update."}, status=200)
        return JsonResponse({"error": form.errors}, status=400)
    return JsonResponse({"error": "An unexpected error occurred"}, status=500)


@login_required()
def unfollow(request: HttpRequest) -> JsonResponse:
    """"View to mark a feed as unfollowed by the user.
    Receive `feedId` as a parameter and update the UserFollowFeed Model

    Parameters
    ----------
    request: HttpRequest

    Returns
    -------
    JsonResponse
    """
    if request.is_ajax and request.method == "POST":
        form = FeedForm(request.POST)
        if form.is_valid():
            feed_id = form.cleaned_data.get("feed_id")
            feed = UserFollowFeed.objects.get(feed_id=feed_id, user_id=request.user.id)
            feed.disabled_at = timezone.now()
            feed.save(update_fields=["disabled_at"])
            return JsonResponse(
                {"message": "The feed was marked as unfollowed."}, status=200
            )
        return JsonResponse({"error": form.errors}, status=400)
    return JsonResponse({"error": "An unexpected error occurred"}, status=500)


@login_required()
def follow(request: HttpRequest) -> JsonResponse:
    """View to mark a feed as followed by the user.
    Receive `feedId` as a parameter and update the UserFollowFeed Model

    Parameters
    ----------
    request: HttpRequest

    Returns
    -------
    JsonResponse
    """
    if request.is_ajax and request.method == "POST":
        form = FeedForm(request.POST)
        if form.is_valid():
            feed_id = form.cleaned_data.get("feed_id")
            feed = UserFollowFeed.objects.get(feed_id=feed_id, user_id=request.user.id)
            feed.disabled_at = None
            feed.save(update_fields=["disabled_at"])
            return JsonResponse(
                {"message": "The feed was marked as followed."}, status=200
            )
        return JsonResponse({"error": form.errors}, status=400)
    return JsonResponse({"error": "An unexpected error occurred"}, status=500)
