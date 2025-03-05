# Useful functions

# Logging API

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

    for name, logger in logging.root.manager.loggerDict.items():
        if name.startswith('pymongo.'):
            logger.setLevel(logging.WARNING)

# Date API

from datetime import datetime

date_formats = [
    '%Y-%m-%d',      #  2022-08-31
    '%Y-%m',         #  2022-08
    '%m/%d/%Y',      #  8/31/2022
    '%m/%d/%y',      #  8/31/22
    '%m/%Y',         #  8/2022
    '%m/%y',         #  8/22
    '%m',            #  8      
    '%b',            #  aug   
    '%Y%m%d',        #  20220831
    '%b %d, %Y',     #  Aug 8, 2024
]

def parse_date(text=None, last_month=False):
    '''
    Parse a date string, return a string of the form YYYY-MM-DD, 
    the format used in the DB.  Possible input formats are defined
    in a global dict named `date_formats`.  

    If no date is specified, use today's date, or, if last_month is True, the
    first day of the previous month.

    Arguments:
        text:  a string with the date to parse (may be None)
        last_month:  if True (and text is None) return the first day of last month
    '''
    if text is None:
        today = datetime.today()
        if last_month:
            m = (today.month - 2) % 12 + 1
            y = today.year if today.month > 1 else today.year - 1
            date = today.replace(year=y, month=m)
        else:
            date = today
    else:
        date = None
        for fmt in date_formats:
            try:
                date = datetime.strptime(text,fmt)
                break
            except Exception:
                pass
        if date is None:
            return None
    
    year = date.year if date.year > 1900 else today.year if date.month <= today.month else today.year - 1

    return f'{year:4d}-{date.month:02d}-{date.day:02d}'
