import pytest
from django.shortcuts import resolve_url
from model_mommy import mommy

from app.models import Feed, Item, UserRelItem
from app.models.user_rel_item import UserRelItemKind


def test_item_list_view_user_not_logged(client):
    response = client.get(resolve_url("list_item", feed_id=2))
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/feed/2/item/"


def test_item_list_view_exception(logged_client):
    with pytest.raises(Exception):
        logged_client.get(resolve_url("list_item", feed_id=2))


def test_item_list_view(logged_client):
    feed = mommy.make(Feed)
    mommy.make(Item, feed_id=feed.id)
    response = logged_client.get(resolve_url("list_item", feed_id=feed.id))
    assert response.status_code == 200
    assert response.resolver_match.url_name == "list_item"
    assert response.context["items"].count() == 1
    assert response.context["feed"].id == feed.id


def test_item_list_view_items_empty(logged_client):
    feed = mommy.make(Feed)
    response = logged_client.get(resolve_url("list_item", feed_id=feed.id))
    assert response.status_code == 200
    assert response.resolver_match.url_name == "list_item"
    assert response.context["items"].count() == 0
    assert response.context["feed"].id == feed.id


def test_mark_as_read_view_user_not_logged(client):
    response = client.get(resolve_url("read"))
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/item/read/"


def test_mark_as_read_view_exception(logged_client):
    with pytest.raises(Exception):
        logged_client.get(resolve_url("read"))


def test_mark_as_read_view(logged_client):
    item = mommy.make(Item)
    response = logged_client.get(resolve_url("read"), data={"itemId": item.id})
    user_id_ = int(logged_client.session._session["_auth_user_id"])
    assert response.status_code == 200
    assert response.resolver_match.url_name == "read"
    assert response.json()["sucess"] == "Item marked as read."
    assert (
        1
        == UserRelItem.objects.filter(
            user_id=user_id_, item_id=item.id, kind=UserRelItemKind.read
        ).count()
    )


def test_add_comment_view_unlogged_user(client):
    response = client.get(resolve_url("add_comment", item_id=3))
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/item/3/comment/"


def test_add_comment_view_logged_user_get_method(logged_client):
    response = logged_client.get(resolve_url("add_comment", item_id=3))
    assert response.status_code == 200
    assert response.resolver_match.url_name == "add_comment"


def test_add_comment_view_logged_user_form_invalid(logged_client):
    response = logged_client.post(resolve_url("add_comment", item_id=3), data={})
    assert response.status_code == 200
    assert response.resolver_match.url_name == "add_comment"
    assert response.context["messages"] == {"comment": ["This field is required."]}


def test_add_comment_view(logged_client):
    item = mommy.make(Item)
    response = logged_client.post(
        resolve_url("add_comment", item_id=item.id), data={"comment": "Test"}
    )
    user_id_ = int(logged_client.session._session["_auth_user_id"])
    assert response.status_code == 200
    assert response.resolver_match.url_name == "add_comment"
    assert (
        1
        == UserRelItem.objects.filter(
            user_id=user_id_, item_id=item.id, kind=UserRelItemKind.comment
        ).count()
    )
