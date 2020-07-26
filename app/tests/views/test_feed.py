from datetime import datetime
from unittest import mock

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


def test_update_feed_view_user_not_logged(client):
    response = client.get(resolve_url("update_feed"))
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/feed/ajax/update/"


def test_update_feed_view_wrong_method(logged_client):
    response = logged_client.get(resolve_url("update_feed"))
    assert response.json() == {"error": "An unexpected error occurred"}
    assert response.status_code == 500


def test_update_feed_view_invalid_form(logged_client):
    response = logged_client.post(resolve_url("update_feed"), data={})
    assert response.status_code == 400
    assert response.resolver_match.url_name == "update_feed"
    assert response.json()["error"] == {"feed_id": ["This field is required."]}


@mock.patch("app.views.feed.update_feed")
def test_mark_as_kind_view_kind_read(update_feed_mock, logged_client):
    feed = baker.make(Feed)
    response = logged_client.post(resolve_url("update_feed"), data={"feed_id": feed.id})
    assert response.status_code == 200
    assert response.resolver_match.url_name == "update_feed"
    assert response.json()["message"] == "The feed was sent to update."
    update_feed_mock.send.assert_called_once_with(feed.id)


def test_add_feed_view_unlogged_user(client):
    response = client.get(resolve_url("add_feed"))
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/feed/add/"


def test_add_feed_view_logged_user_get_method(logged_client):
    response = logged_client.get(resolve_url("add_feed"))
    assert response.status_code == 200
    assert response.resolver_match.url_name == "add_feed"


def test_add_feed_view_logged_user_form_invalid(logged_client):
    response = logged_client.post(resolve_url("add_feed"), data={})
    assert response.status_code == 200
    assert response.resolver_match.url_name == "add_feed"
    assert response.context["messages"] == {"url": ["This field is required."]}


@mock.patch("app.views.feed.parse_feed")
def test_add_feed_view(parse_feed_mock, logged_client):
    response = logged_client.post(resolve_url("add_feed"), data={"url": "test.com"})
    user_id_ = int(logged_client.session._session["_auth_user_id"])
    assert response.status_code == 200
    assert response.resolver_match.url_name == "add_feed"
    parse_feed_mock.send.assert_called_once_with("http://test.com", "", user_id_)
