from datetime import datetime

import dramatiq
import feedparser
from django.conf import settings

from app.models.feed import Feed
from app.models.user_follow_feed import UserFollowFeed
from app.utils import create_items

DATE_FORMAT = "%a, %d %b %Y %X %z"
DATE_FORMAT_2 = "%a, %d %b %Y %X %Z"

MAX_RETRIES = settings.DRAMATIQ_MAX_RETRIES


@dramatiq.actor(max_retries=MAX_RETRIES)
def parse_feed(url: str, alias: str, user_id: int) -> None:
    """

    :param url:
    :param alias:
    :param user_id:
    :return:
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
        raise e


@dramatiq.actor(max_retries=MAX_RETRIES)
def follow_feed(feed_id: int, user_id: int) -> None:
    """

    :param feed_id:
    :param user_id:
    :return:
    """
    try:
        UserFollowFeed.objects.create(feed_id=feed_id, user_id=user_id)
    except Exception as e:
        raise e


@dramatiq.actor(max_retries=MAX_RETRIES)
def parse_entries(url: str, feed_id: int) -> None:
    """

    :param url:
    :param feed_id:
    :return:
    """
    try:
        parsed_entries = feedparser.parse(url)
        parsed_entries = parsed_entries.entries
        create_items(feed_id, parsed_entries)
    except Exception as e:
        raise e


@dramatiq.actor(max_retries=MAX_RETRIES)
def update_feed(feed_id: int) -> None:
    """

    :param feed_id:
    :return:
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
        raise e
