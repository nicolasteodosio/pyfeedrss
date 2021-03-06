"""pyfeedrss URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path

from app.views import feed, item, main

urlpatterns = [
    path("admin/", admin.site.urls),
    url(r"^home/$", main.home, name="home"),
    url(r"^$", main.home, name="home"),
    url(r"^signup/$", main.signup, name="signup"),
    url(r"sentry-debug/$", main.trigger_error, name="tigger_error"),
    url(r"^feed/add/$", feed.add, name="add_feed"),
    url(r"^feed/list/$", feed.list, name="list_feed"),
    url(r"^feed/ajax/update/$", feed.update, name="update_feed"),
    url(r"^feed/ajax/follow/$", feed.follow, name="follow_feed"),
    url(r"^feed/ajax/unfollow/$", feed.unfollow, name="unfollow_feed"),
    url(r"^feed/update/all$", feed.update, name="update_all"),
    path("feed/<int:feed_id>/item/", item.list, name="list_item"),
    path("item/<int:item_id>/comment/", item.add_comment, name="add_comment"),
    url("item/ajax/mark", item.mark_as_kind, name="mark_item"),
    path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
