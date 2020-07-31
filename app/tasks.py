from datetime import datetime

import dramatiq
import feedparser
from django.conf import settings

from app.exceptions import (
    FollowFeedError,
    ParseEntriesError,
    ParseFeedError,
    UpdateFeedError,
)
from app.models.feed import Feed
from app.models.user_follow_feed import UserFollowFeed
from app.utils import create_items

DATE_FORMAT = "%a, %d %b %Y %X %z"
DATE_FORMAT_2 = "%a, %d %b %Y %X %Z"

MAX_RETRIES = settings.DRAMATIQ_MAX_RETRIES


@dramatiq.actor(max_retries=MAX_RETRIES)
def parse_feed(url: str, alias: str, user_id: int) -> None:
    """Task responsible for parse the feed url.
    Check if that feed is already created in database, if not create.
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
            "description": parsed.description,
            "ttl": parsed_feed.ttl,
            "last_build_date": datetime.strptime(parsed.modified, DATE_FORMAT_2,),
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
    Call `create_items` to create in the dabatase

    Parameters
    ----------
    url: str
        Url feed to get entries
    feed_id: innt
        Feed id
    Returns
    -------

    """
    try:
        parsed_entries = feedparser.parse(url)
        parsed_entries = parsed_entries.entries
        create_items(feed_id, parsed_entries)
    except Exception as e:
        raise ParseEntriesError from e


@dramatiq.actor(max_retries=MAX_RETRIES)
def update_feed(feed_id: int) -> None:
    """Task responsible to check and update a feed if necessary.
    Call `create_items` if has new item to create

    Parameters
    ----------
    feed_id: int
        Feed id
    Returns
    -------

    """
    try:
        feed = Feed.objects.get(id=feed_id)

        parsed_feed = feedparser.parse(
            feed.link, modified=feed.last_build_date.strftime(DATE_FORMAT_2)
        )
        if parsed_feed.status == 304:
            return

        feed.last_build_date = datetime.strptime(parsed_feed.modified, DATE_FORMAT_2)
        feed.save(update_fields=["last_build_date"])

        parsed_entries = parsed_feed.entries

        create_items(feed_id, parsed_entries)
    except Exception as e:
        raise UpdateFeedError from e
