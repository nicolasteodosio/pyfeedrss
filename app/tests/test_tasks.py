from datetime import datetime
from unittest import mock
from unittest.mock import Mock

import pytest
from django.contrib.auth.models import User
from django.utils.timezone import now
from freezegun import freeze_time
from model_bakery import baker

from app.exceptions import (
    FollowFeedError,
    ParseEntriesError,
    ParseFeedError,
    UpdateFeedError,
)
from app.models import Feed, Item, UserFollowFeed
from app.tasks import follow_feed, parse_entries, parse_feed, update_feed


class FeedMock(object):
    def __init__(self, ttl, title, modified_parsed, **kwargs):
        self.ttl = ttl
        self.title = title
        self.modified_parsed = modified_parsed.timetuple()


@freeze_time("2020-07-24")
@pytest.mark.django_db(transaction=True)
@mock.patch("app.tasks.parse_entries")
@mock.patch("app.tasks.follow_feed")
def test_parse_feed(follow_feed_mock, parse_entries_mock, broker, worker):
    user = baker.make(User)

    with mock.patch("app.tasks.feedparser") as mock_parser:
        mock_feed_dict = Mock(
            feed=FeedMock(
                ttl=60,
                title="Test",
                modified_parsed=datetime.now(),
                kwargs={
                    "title": "Test",
                    "links": [{"test": "test"}, {"test": "test", "href": "test.com"}],
                    "ttl": 60,
                    "link": "la",
                    "updated": "Fri, 24 Jul 2020 15:38:57 GMT",
                },
            ),
            href="test.com",
            description="test",
            modified="Fri, 24 Jul 2020 15:38:57 GMT",
        )

        mock_parser.parse.return_value = mock_feed_dict
        parse_feed.send("test.com", "test", user.id)

        broker.join(parse_feed.queue_name)
        worker.join()

        feed_obj = Feed.objects.get(title=mock_feed_dict.feed.title)

        follow_feed_mock.send.assert_called_once_with(feed_obj.id, user.id)
        parse_entries_mock.send.assert_called_once_with("test.com", feed_obj.id)
        assert Feed.objects.filter(title=mock_feed_dict.feed.title).count() == 1


@freeze_time("2020-07-24")
@pytest.mark.django_db(transaction=True)
@mock.patch("app.tasks.parse_entries")
@mock.patch("app.tasks.follow_feed")
def test_parse_feed_already_created(
    follow_feed_mock, parse_entries_mock, broker, worker
):
    user = baker.make(User)
    baker.make(Feed, title="Test")

    with mock.patch("app.tasks.feedparser") as mock_parser:
        mock_feed_dict = Mock(
            feed=FeedMock(
                ttl=60,
                title="Test",
                modified_parsed=datetime.now(),
                kwargs={
                    "title": "Test",
                    "links": [{"test": "test"}, {"test": "test", "href": "test.com"}],
                    "ttl": 60,
                    "link": "la",
                    "updated": "Fri, 24 Jul 2020 15:38:57 GMT",
                },
            ),
            href="test.com",
            description="",
            modified="Fri, 24 Jul 2020 15:38:57 GMT",
        )

        mock_parser.parse.return_value = mock_feed_dict
        parse_feed.send("test.com", "test", user.id)

        broker.join(parse_feed.queue_name)
        worker.join()

        feed_obj = Feed.objects.get(title=mock_feed_dict.feed.title)

        follow_feed_mock.send.assert_called_once_with(feed_obj.id, user.id)
        parse_entries_mock.assert_not_called()
        assert Feed.objects.filter(title=mock_feed_dict.feed.title).count() == 1


@pytest.mark.django_db(transaction=True)
@mock.patch("app.tasks.parse_entries")
@mock.patch("app.tasks.follow_feed")
@mock.patch("app.tasks.feedparser")
def test_parse_feed_exception(
    mock_parser, follow_feed_mock, parse_entries_mock, broker, worker
):
    user = baker.make(User)
    mock_parser.parse.side_effect = Exception("error")
    with pytest.raises(ParseFeedError):
        parse_feed.send("test.com", "test", user.id)
        broker.join(parse_feed.queue_name, fail_fast=True)
        worker.join()

    follow_feed_mock.send.assert_not_called()
    parse_entries_mock.send.assert_not_called()
    assert Feed.objects.all().count() == 0


@pytest.mark.django_db(transaction=True)
def test_follow_feed(broker, worker):
    feed = baker.make(Feed)
    user = baker.make(User)
    follow_feed.send(feed.id, user.id)
    broker.join(follow_feed.queue_name)
    worker.join()

    assert UserFollowFeed.objects.filter(feed_id=feed.id, user_id=user.id).exists()


@pytest.mark.django_db(transaction=True)
def test_follow_feed_feed_dont_exist(broker, worker):
    user = baker.make(User)
    with pytest.raises(FollowFeedError):
        follow_feed.send(123, user.id)
        broker.join(follow_feed.queue_name, fail_fast=True)
        worker.join()


@pytest.mark.django_db(transaction=True)
def test_follow_feed_user_dont_exist(broker, worker):
    feed = baker.make(Feed)
    with pytest.raises(FollowFeedError):
        follow_feed.send(feed.id, 456)
        broker.join(follow_feed.queue_name, fail_fast=True)
        worker.join()


@pytest.mark.django_db(transaction=True)
@mock.patch("app.tasks.create_items")
@mock.patch("app.tasks.feedparser")
def test_parse_entries(mock_parser, mock_create_items, broker, worker):
    mock_entries_dict = Mock(
        entries={
            "title": "Test",
            "links": [{"test": "test"}, {"test": "test", "href": "test.com"}],
            "ttl": 60,
            "summary": "Mysummary test",
            "updated": "Fri, 24 Jul 2020 15:38:57 GMT",
        }
    )
    mock_parser.parse.return_value = mock_entries_dict
    feed = baker.make(Feed)
    parse_entries.send("teste.com", feed.id)
    broker.join(parse_entries.queue_name)
    worker.join()
    mock_create_items.assert_called_once_with(
        feed.id,
        {
            "title": "Test",
            "links": [{"test": "test"}, {"test": "test", "href": "test.com"}],
            "ttl": 60,
            "summary": "Mysummary test",
            "updated": "Fri, 24 Jul 2020 15:38:57 GMT",
        },
    )


@pytest.mark.django_db(transaction=True)
@mock.patch("app.tasks.create_items")
@mock.patch("app.tasks.feedparser")
def test_parse_entries_exception(mock_parser, mock_create_items, broker, worker):
    mock_parser.parse.side_effect = Exception("error")
    feed = baker.make(Feed)
    with pytest.raises(ParseEntriesError):
        parse_entries.send("teste.com", feed.id)
        broker.join(parse_entries.queue_name, fail_fast=True)
        worker.join()
    mock_create_items.assert_not_called()


@pytest.mark.django_db(transaction=True)
@mock.patch("app.tasks.create_items")
@mock.patch("app.tasks.feedparser")
def test_update_feed(mock_parser, mock_create_items, broker, worker):
    feed = baker.make(Feed, last_build_date=now)
    baker.make(Item, feed=feed, _quantity=10)
    mock_entries_dict = Mock(
        feed=FeedMock(
            ttl=60,
            title="Test",
            modified_parsed=datetime.now(),
            kwargs={
                "title": "Test",
                "links": [{"test": "test"}, {"test": "test", "href": "test.com"}],
                "ttl": 60,
                "link": "la",
                "updated": "Fri, 24 Jul 2020 15:38:57 GMT",
            },
        ),
        status=301,
        modified="Fri, 24 Jul 2020 15:38:57 GMT",
        modified_parsed=datetime.now().timetuple(),
        entries=[
            {
                "title": "Test",
                "links": [{"test": "test"}, {"test": "test", "href": "test.com"}],
                "ttl": 60,
                "summary": "Mysummary test",
                "updated": "Fri, 24 Jul 2020 15:38:57 GMT",
            },
        ],
    )
    mock_parser.parse.return_value = mock_entries_dict
    update_feed.send(feed.id)
    broker.join(update_feed.queue_name)
    worker.join()
    mock_create_items.assert_called_once_with(
        feed.id,
        [
            {
                "title": "Test",
                "links": [{"test": "test"}, {"test": "test", "href": "test.com"}],
                "ttl": 60,
                "summary": "Mysummary test",
                "updated": "Fri, 24 Jul 2020 15:38:57 GMT",
            }
        ],
    )
    assert Feed.objects.get(id=feed.id).last_build_date != feed.last_build_date


@pytest.mark.django_db(transaction=True)
@mock.patch("app.tasks.create_items")
@mock.patch("app.tasks.feedparser")
def test_update_feed_exception(mock_parser, mock_create_items, broker, worker):
    feed = baker.make(Feed, last_build_date=now)
    baker.make(Item, feed=feed, _quantity=10)
    mock_parser.parse.side_effect = Exception
    with pytest.raises(UpdateFeedError):
        update_feed.send(feed.id)
        broker.join(update_feed.queue_name, fail_fast=True)
        worker.join()
    mock_create_items.assert_not_called()


@pytest.mark.django_db(transaction=True)
@mock.patch("app.tasks.create_items")
@mock.patch("app.tasks.feedparser")
def test_update_feed_status_is_304(mock_parser, mock_create_items, broker, worker):
    feed = baker.make(Feed, last_build_date=now)
    baker.make(Item, feed=feed, _quantity=10)
    mock_entries_dict = Mock(
        feed={}, status=304, modified="Fri, 24 Jul 2020 15:38:57 GMT", entries=[]
    )
    mock_parser.parse.return_value = mock_entries_dict
    update_feed.send(feed.id)
    broker.join(update_feed.queue_name)
    worker.join()
    mock_create_items.assert_not_called()
