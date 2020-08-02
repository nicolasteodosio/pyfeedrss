from datetime import datetime
from time import mktime

import dramatiq
import feedparser
from django.conf import settings

from app.exceptions import (
    FollowFeedError,
    ParseEntriesError,
    ParseFeedError,
    UpdateFeedError,
)
from app.models import Item, Notification
from app.models.feed import Feed
from app.models.user_follow_feed import UserFollowFeed

DATE_FORMAT = "%a, %d %b %Y %X %Z"

MAX_RETRIES = settings.DRAMATIQ_MAX_RETRIES


@dramatiq.actor(max_retries=MAX_RETRIES)
def parse_feed(url: str, alias: str, user_id: int) -> None:
    """Task responsible for parse the feed url.
    Check if that feed is already created in database, if not, create.
    Call `dramatiq.actor` task follow_feed and parse_entries.

    Parameters
    ----------
    url: str
        Feed url

    alias: str
        Alias of the feed, optional.

    user_id: int
        Id of the user
    Returns
    -------

    """
    try:
        parsed = feedparser.parse(url)
        parsed_feed = parsed.feed
        feed_dict = {
            "link": parsed.href,
            "description": getattr(parsed, "description", None),
            "ttl": getattr(parsed_feed, "ttl", 0),
            "etag": getattr(parsed, "etag", None),
            "last_build_date": datetime.fromtimestamp(
                mktime(parsed_feed.modified_parsed)
            ),
        }
        feed_object, created = Feed.objects.get_or_create(
            title=parsed_feed.title, defaults=feed_dict
        )

        follow_feed.send(feed_object.id, user_id)
        if created:
            parse_entries.send(url, feed_object.id)
    except Exception as e:
        raise ParseFeedError from e


@dramatiq.actor(max_retries=MAX_RETRIES)
def follow_feed(feed_id: int, user_id: int) -> None:
    """Task responsible for creating a UserFollowFeed register in database

    Parameters
    ----------
    feed_id: int
        Feed id
    user_id: int
        User id
    Returns
    -------

    """
    try:
        UserFollowFeed.objects.create(feed_id=feed_id, user_id=user_id)
    except Exception as e:
        raise FollowFeedError from e


@dramatiq.actor(max_retries=MAX_RETRIES)
def parse_entries(url: str, feed_id: int) -> None:
    """Task responsible to parse entries from the url feed.
    Call `bulk_entries_create` to create in the dabatase

    Parameters
    ----------
    url: str
        Url feed to get entries
    feed_id: int
        Feed id
    Returns
    -------

    """
    try:
        parsed_entries = feedparser.parse(url)
        parsed_entries = parsed_entries.entries
        Item.objects.bulk_entries_create(feed_id, parsed_entries)
    except Exception as e:
        raise ParseEntriesError from e


@dramatiq.actor(max_retries=MAX_RETRIES)
def update_feed(feed_id: int, user_id: int) -> None:
    """Task responsible to check and update a feed if necessary.
    Call `bulk_entries_create` if has new item to create

    Parameters
    ----------
    feed_id: int
        Feed id
    user_id: int
        User id
    Returns
    -------

    Error
    -----
        If an error is triggered a Notification is created only once.
    """
    try:
        feed = Feed.objects.get(id=feed_id)

        if feed.etag:
            parsed_feed = feedparser.parse(feed.link, etag=feed.etag)
        else:
            parsed_feed = feedparser.parse(
                feed.link, modified=feed.last_build_date.strftime(DATE_FORMAT)
            )
        if parsed_feed.status == 304:
            return

        feed.etag = getattr(parsed_feed, "etag", None)
        feed.last_build_date = datetime.fromtimestamp(
            mktime(parsed_feed.feed.modified_parsed)
        )
        feed.save(update_fields=["last_build_date", "etag"])

        parsed_entries = parsed_feed.entries

        Item.objects.bulk_entries_create(feed_id, parsed_entries)
    except Exception as e:
        Notification.objects.get_or_create(
            user_id=user_id,
            content=f"Feed {feed_id} was not updated, try again latter",
            defaults={"read": False},
        )
        raise UpdateFeedError from e
