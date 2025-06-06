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
        format='%(message)s',
        handlers = [RichHandler(markup=True, rich_tracebacks=True)],
    )

    for name, logger in logging.root.manager.loggerDict.items():
        if name.startswith('pymongo.'):
            logger.setLevel(logging.WARNING)

# Return True if the log level is set to DEBUG

def debugging():
    return logging.getLogger().level <= logging.DEBUG


# Date API

from datetime import date, datetime
import calendar

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
    Parse a date string.  Possible input formats are defined in a global dict 
    named `date_formats`.  

    If no date is specified, use today's date, or, if last_month is True, the
    first day of the previous month.

    Raises an exception if the text does not match any of the formats or if
    the date values are not a valid combination (e.g. "2024-02-30").

    Arguments:
        text:  a string with the date to parse (may be None)
        last_month:  if True (and text is None) return the first day of last month
    '''
    today = date.today()

    if text is None:
        if last_month:
            m = (today.month - 2) % 12 + 1
            y = today.year if today.month > 1 else today.year - 1
            res = today.replace(year=y, month=m)
        else:
            res = today
    else:
        res = None
        for fmt in date_formats:
            try:
                res = datetime.strptime(text,fmt)
                break
            except Exception:
                pass
        else:
            raise ValueError(f'parse_date: unable to parse {text}')
    
    year = res.year if res.year > 1900 else today.year if res.month <= today.month else today.year - 1

    return date(year, res.month, res.day)

def date_range(month, year=None):
    '''Return the first and last day of a month (three-letter abbreviation)'''
    today = date.today()
    m = datetime.strptime(month.lower(),'%b').month
    y = year or (today.year if m < today.month else today.year - 1)
    _, last = calendar.monthrange(y,m)
    return date(y,m,1), date(y,m,last)
