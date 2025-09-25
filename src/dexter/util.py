# Useful functions

########
#
# Use "with cd(X)"" to execute a shell command in directory X
#

import os

class cd:
    "context manager for changing the working directory"
    def __init__(self, path):
        self._new_dir = path

    def __enter__(self):
        self._old_dir = os.getcwd()
        os.chdir(self._new_dir)

    def __exit__(self, *ignored):
        os.chdir(self._old_dir)

# Logging API

import calendar
from datetime import date, datetime

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
        handlers = [RichHandler(markup=True, rich_tracebacks=True, show_time=False, show_path=(arg=='debug'))],
    )

    for name, logger in logging.root.manager.loggerDict.items():
        if name.startswith('pymongo.'):
            logger.setLevel(logging.WARNING)

# Return True if the log level is set to DEBUG

def debugging():
    return logging.getLogger().level <= logging.DEBUG


# Date API

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

def parse_date(text):
    '''
    Parse a date string.  Possible input formats are defined in a global dict 
    named `date_formats`.  

    Raises an exception if the text does not match any of the formats or if
    the date values are not a valid combination (e.g. "2024-02-30").

    Arguments:
        text:  a string with the date to parse
    '''
    res = None
    for fmt in date_formats:
        try:
            res = datetime.strptime(text,fmt)
            break
        except Exception:
            pass
    else:
        raise ValueError(f'parse_date: unable to parse {text}')

    today = date.today()
    year = res.year if res.year > 1900 else today.year if res.month <= today.month else today.year - 1

    return date(year, res.month, res.day)

def date_range(month, year=None):
    '''
    Return the first and last day of a month (three-letter abbreviation)
    '''
    today = date.today()
    m = datetime.strptime(month.lower(),'%b').month
    y = year or (today.year if m < today.month else today.year - 1)
    _, last = calendar.monthrange(y,m)
    return date(y,m,1), date(y,m,last)

