from .base import *  # noqa

LOGGING["formatters"]["standard"] = {  # noqa: F405
    "()": "nicelog.formatters.Colorful",
    "show_date": True,
    "show_function": True,
    "show_filename": True,
    "message_inline": False,
}
