class Error(Exception):
    """Base class for other exceptions"""

    pass


class ParseFeedError(Error):
    """Class for parse_feed exceptions"""

    pass


class FollowFeedError(Error):
    """Class for follow_feed exceptions"""

    pass


class ParseEntriesError(Error):
    """Class for parse_entries exceptions"""

    pass


class UpdateFeedError(Error):
    """Class for update_feed exceptions"""

    pass
