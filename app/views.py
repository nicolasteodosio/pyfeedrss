from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from app.forms import AddFeedForm
from app.tasks import parse_feed


def signup(request: HttpRequest) -> HttpResponse:
    """
    SignUp view, if user is valid and authenticated redirect to home
    :param request:HttpRequest

    :return: HttpResponse
        rendered signup page
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def home(request: HttpRequest) -> HttpResponse:
    """
    Home View
    :param request:HttpRequest
    :return: HttpResponse
        rendered home page
    """
    return render(request, "home.html")


@login_required()
def add_feed(request: HttpRequest) -> HttpResponse:
    """

    :param request:
    :return:
    """
    if request.method == "POST":
        form = AddFeedForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get("url")
            alias = form.cleaned_data.get("alias")
            parse_feed(url, alias)
    else:
        form = AddFeedForm()
    return render(request, "add_feed.html", {"form": form})
