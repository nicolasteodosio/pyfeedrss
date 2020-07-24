from datetime import datetime

from app.models import Item

DATE_FORMAT_2 = "%a, %d %b %Y %X %Z"


def create_items(feed_id, parsed_entries):
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
