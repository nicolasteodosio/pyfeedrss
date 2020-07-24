from datetime import datetime

import dramatiq
import feedparser

from app.models.feed import Feed
from app.models.item import Item
from app.models.user_follow_feed import UserFollowFeed

DATE_FORMAT = "%a, %d %b %Y %X %z"

MAX_RETRIES = 3


@dramatiq.actor(max_retries=MAX_RETRIES)
def parse_feed(url: str, alias: str, user_id: int) -> None:
    """

    :param url:
    :param alias:
    :param user_id:
    :return:
    """
    try:
        parsed_feed = feedparser.parse(url)
        parsed_feed = parsed_feed["feed"]
        feed_dict = {
            "link": parsed_feed["links"][1]["href"],
            "descritpion": parsed_feed["link"],
            "ttl": parsed_feed["ttl"],
            "last_build_date": datetime.strptime(parsed_feed["updated"], DATE_FORMAT,),
        }
        feed_object, created = Feed.objects.get_or_create(
            title=parsed_feed["title"], defaults=feed_dict
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
        parsed_entries = parsed_entries["entries"]
        entries_to_create = []
        for entry in parsed_entries:
            entries_to_create.append(
                Item(
                    feed_id=feed_id,
                    title=entry["title"],
                    link=entry["link"],
                    descritpion=entry["summary"],
                    published_at=datetime.strptime(entry["published"], DATE_FORMAT),
                )
            )

        Item.objects.bulk_create(entries_to_create)
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

        recent_item_date = (
            Item.objects.filter(feed_id=feed.id).earliest("published_at").published_at
        )

        parsed_feed = feedparser.parse(feed.link)

        feed.last_build_date = (
            datetime.strptime(parsed_feed["updated"], DATE_FORMAT,),
        )
        feed.save()

        parsed_entries = parsed_feed["entries"]

        filtered_entries = [
            d
            for d in parsed_entries
            if datetime.strptime(d["published"], DATE_FORMAT) > recent_item_date
        ]
        entries_to_create = []

        for entry in filtered_entries:
            entry_published = datetime.strptime(entry["published"], DATE_FORMAT)
            entries_to_create.append(
                Item(
                    feed_id=feed_id,
                    title=entry["title"],
                    link=entry["link"],
                    descritpion=entry["summary"],
                    published_at=entry_published,
                )
            )

        Item.objects.bulk_create(entries_to_create)
    except Exception as e:
        raise e
