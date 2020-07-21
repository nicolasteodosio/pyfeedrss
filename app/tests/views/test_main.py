import pytest
from django.shortcuts import resolve_url


def test_home_view(client):
    response = client.get(resolve_url("home"))
    assert response.status_code == 200


def test_signup_view_get_request(client):
    response = client.get(resolve_url("signup"))
    assert response.status_code == 200
    assert response.resolver_match.url_name == "signup"


@pytest.mark.django_db
def test_signup_view_post_error_missing_parameter(client):
    response = client.post(
        resolve_url("signup"), data={"username": "test", "password": "test"}
    )
    assert response.status_code == 200
    assert response.resolver_match.url_name == "signup"


@pytest.mark.django_db
def test_signup_view_create_user(client):
    response = client.post(
        resolve_url("signup"),
        data={
            "username": "test",
            "password1": "aletariosenha123",
            "password2": "aletariosenha123",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert response.resolver_match.url_name == "home"
