from datetime import datetime
from typing import List

from app.models import Item

DATE_FORMAT_2 = "%a, %d %b %Y %X %Z"


def create_items(feed_id: int, parsed_entries: List) -> None:
    """Function responsible for creating items in the database

    Parameters
    ----------
    feed_id: int
        Feed id
    parsed_entries: List
        List with entries to be created in the database

    Returns
    -------

    """
    entries_to_create = []
    for entry in parsed_entries:
        entries_to_create.append(
            Item(
                feed_id=feed_id,
                title=entry["title"],
                link=entry["link"],
                descritpion=entry["summary"],
                published_at=datetime.strptime(entry["published"], DATE_FORMAT_2),
            )
        )
    Item.objects.bulk_create(entries_to_create)
