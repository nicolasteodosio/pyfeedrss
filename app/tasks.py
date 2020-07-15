from datetime import datetime

import feedparser

from app.models.feed import Feed


def parse_feed(url: str, alias: str) -> None:
    """

    :param url:
    :param alias:
    :return:
    """
    parsed_feed = feedparser.parse(url)
    parsed_feed = parsed_feed["feed"]
    feed_dict = {
        "title": parsed_feed["title"],
        "link": parsed_feed["link"],
        "descritpion": parsed_feed["link"],
        "ttl": parsed_feed["ttl"],
        "last_build_date": datetime.now(),
    }
    Feed.objects.create(**feed_dict)
    print(parsed_feed)
