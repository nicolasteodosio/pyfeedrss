from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def signup(request: HttpRequest) -> HttpResponse:
    """ SignUp view, if user is valid and authenticated redirect to home

    Parameters
    ----------
    request: HttpRequest

    Returns
    -------
    rendered signup page
    """

    try:
        if request.method == "POST":
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password1")
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect("home")
            else:
                return render(
                    request,
                    "registration/signup.html",
                    {"form": form, "messages": form.errors},
                )
        else:
            form = UserCreationForm()
        return render(request, "registration/signup.html", {"form": form})
    except Exception as e:
        raise e


def home(request: HttpRequest) -> HttpResponse:
    """

    Parameters
    ----------
    request: HttpRequest

    Returns
    -------
    rendered home page
    """

    return render(request, "home.html")


def trigger_error(request: HttpRequest):
    """View to debug sentry integration

    Parameters
    ----------
    request

    Returns
    -------

    """
    try:
        1 / 0
    except Exception as e:
        raise e
