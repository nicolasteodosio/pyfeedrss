import pytest
from django.shortcuts import resolve_url
from model_bakery import baker

from app.models import Feed, Item, UserRelItem
from app.models.user_rel_item import UserRelItemKind


def test_item_list_view_user_not_logged(client):
    response = client.get(resolve_url("list_item", feed_id=2))
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/feed/2/item/"


def test_item_list_view_feed_dont_exists(logged_client):
    response = logged_client.get(resolve_url("list_item", feed_id=789456))
    assert response.status_code == 404


def test_item_list_view_exception(logged_client):
    with pytest.raises(Exception):
        logged_client.get(resolve_url("list_item", feed_id="error"))


def test_item_list_view(logged_client):
    feed = baker.make(Feed)
    baker.make(Item, feed_id=feed.id)
    response = logged_client.get(resolve_url("list_item", feed_id=feed.id))
    assert response.status_code == 200
    assert response.resolver_match.url_name == "list_item"
    assert response.context["items"].count() == 1
    assert response.context["feed"].id == feed.id


def test_item_list_view_items_empty(logged_client):
    feed = baker.make(Feed)
    response = logged_client.get(resolve_url("list_item", feed_id=feed.id))
    assert response.status_code == 200
    assert response.resolver_match.url_name == "list_item"
    assert response.context["items"].count() == 0
    assert response.context["feed"].id == feed.id


def test_mark_as_kind_view_user_not_logged(client):
    response = client.get(resolve_url("mark_item"))
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/item/ajax/mark"


def test_mark_as_kind_view_wrong_method(logged_client):
    response = logged_client.get(resolve_url("mark_item"))
    assert response.json() == {"error": "An unexpected error occurred"}
    assert response.status_code == 500


def test_mark_as_kind_view_invalid_form(logged_client):
    item = baker.make(Item)
    response = logged_client.post(resolve_url("mark_item"), data={"item_id": item.id})
    assert response.status_code == 400
    assert response.resolver_match.url_name == "mark_item"
    assert response.json()["error"] == {"kind": ["This field is required."]}


def test_mark_as_kind_view_kind_read(logged_client):
    item = baker.make(Item)
    response = logged_client.post(
        resolve_url("mark_item"), data={"item_id": item.id, "kind": "read"}
    )
    user_id_ = int(logged_client.session._session["_auth_user_id"])
    assert response.status_code == 200
    assert response.resolver_match.url_name == "mark_item"
    assert response.json()["message"] == "The item was marked as read."
    assert (
        1
        == UserRelItem.objects.filter(
            user_id=user_id_, item_id=item.id, kind=UserRelItemKind.read
        ).count()
    )


def test_mark_as_kind_view_kind_favorite(logged_client):
    item = baker.make(Item)
    response = logged_client.post(
        resolve_url("mark_item"), data={"item_id": item.id, "kind": "favorite"}
    )
    user_id_ = int(logged_client.session._session["_auth_user_id"])
    assert response.status_code == 200
    assert response.resolver_match.url_name == "mark_item"
    assert response.json()["message"] == "The item was marked as favorite."
    assert (
        1
        == UserRelItem.objects.filter(
            user_id=user_id_, item_id=item.id, kind=UserRelItemKind.favorite
        ).count()
    )


def test_mark_as_kind_view_kind_unfavorite(logged_client):
    user_id_ = int(logged_client.session._session["_auth_user_id"])
    item = baker.make(Item)
    baker.make(
        UserRelItem,
        kind=UserRelItemKind.favorite,
        user_id=user_id_,
        disabled_at=None,
        item=item,
    )
    response = logged_client.post(
        resolve_url("mark_item"), data={"item_id": item.id, "kind": "unfavorite"}
    )
    assert response.status_code == 200
    assert response.resolver_match.url_name == "mark_item"
    assert response.json()["message"] == "The item was marked as unfavorite."
    assert (
        0
        == UserRelItem.objects.filter(
            user_id=user_id_,
            item_id=item.id,
            kind=UserRelItemKind.favorite,
            disabled_at__isnull=True,
        ).count()
    )


def test_mark_as_kind_view_kind_unfavorite_no_fav_exists(logged_client):
    user_id_ = int(logged_client.session._session["_auth_user_id"])
    item = baker.make(Item)
    response = logged_client.post(
        resolve_url("mark_item"), data={"item_id": item.id, "kind": "unfavorite"}
    )
    assert response.status_code == 200
    assert response.resolver_match.url_name == "mark_item"
    assert response.json()["message"] == "The item was marked as unfavorite."
    assert (
        0
        == UserRelItem.objects.filter(
            user_id=user_id_,
            item_id=item.id,
            kind=UserRelItemKind.favorite,
            disabled_at__isnull=True,
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
    item = baker.make(Item)
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
