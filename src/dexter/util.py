# Useful functions

import logging
from rich.logging import RichHandler

def setup_logging(arg):
    """
    Configure the logging modile.
    """
    match arg:
        case 'info':
            level = logging.INFO
        case 'debug':
            level = logging.DEBUG
        case _:
            level = logging.WARNING
    logging.basicConfig(
        level=level,
        style='{',
        format='{relativeCreated:4.0f} msec: {message}',
        handlers = [RichHandler(markup=True, rich_tracebacks=True)],
    )
