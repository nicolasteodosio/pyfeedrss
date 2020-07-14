from django.shortcuts import resolve_url


def test_home_view(client):
    response = client.get(resolve_url("home"))
    assert response.status_code == 200


def test_signup_view_get_request(client):
    response = client.get(resolve_url("signup"))
    assert response.status_code == 200
