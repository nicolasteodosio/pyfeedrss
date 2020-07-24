from datetime import datetime

import pytest
from django.shortcuts import resolve_url
from model_bakery import baker

from app.models import Feed, UserFollowFeed


def test_feed_list_view_user_not_logged(client):
    response = client.get(resolve_url("list_feed"))
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/feed/list/"


def test_feed_list_view_empty(logged_client):
    response = logged_client.get(resolve_url("list_feed"))
    assert response.status_code == 200
    assert response.resolver_match.url_name == "list_feed"
    assert list(response.context["feeds_followed"]) == []
    assert list(response.context["feeds_unfollowed"]) == []


@pytest.mark.django_db
def test_feed_list_view(logged_client):
    feeds = baker.make(Feed, _quantity=2)
    user_id_ = int(logged_client.session._session["_auth_user_id"])
    baker.make(UserFollowFeed, feed_id=feeds[0].id, user_id=user_id_)
    baker.make(
        UserFollowFeed,
        feed_id=feeds[1].id,
        user_id=user_id_,
        disabled_at=datetime.now(),
    )
    response = logged_client.get(resolve_url("list_feed"))
    assert response.status_code == 200
    assert response.resolver_match.url_name == "list_feed"
    assert response.context["feeds_followed"].count() == 1
    assert response.context["feeds_unfollowed"].count() == 1
