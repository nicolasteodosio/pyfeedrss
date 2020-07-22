from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from app.forms import AddFeedForm
from app.models.feed import Feed
from app.models.user_follow_feed import UserFollowFeed
from app.tasks import parse_feed, update_feed


@login_required()
def add(request: HttpRequest) -> HttpResponse:
    """

    :param request:
    :return:
    """
    if request.method == "POST":
        form = AddFeedForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get("url")
            alias = form.cleaned_data.get("alias")
            parse_feed(url, alias, request.user.id)
    else:
        form = AddFeedForm()
    return render(request, "add_feed.html", {"form": form})


@login_required()
def list(request: HttpRequest) -> HttpResponse:
    """

    :param request:
    :return:
    """
    user_id = request.user.id
    users_follow_feed_id = UserFollowFeed.followed.filter(user_id=user_id).values_list(
        "feed_id", flat=True
    )
    users_unfollow_feed_id = UserFollowFeed.unfollowed.filter(
        user_id=user_id
    ).values_list("feed_id", flat=True)
    feeds_followed = Feed.objects.filter(id__in=users_follow_feed_id)
    feeds_unfollowed = Feed.objects.filter(id__in=users_unfollow_feed_id)

    return render(
        request,
        "list_feed.html",
        {"feeds_followed": feeds_followed, "feeds_unfollowed": feeds_unfollowed},
    )


@login_required()
def update(request: HttpRequest) -> JsonResponse:
    try:
        feed_id = request.GET.get("feedId")
        update_feed(feed_id)
        return JsonResponse({"data": "success"})
    except Exception as e:
        raise e
