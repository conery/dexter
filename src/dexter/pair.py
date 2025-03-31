#  Method for pairing entries to create transactions

import logging
import re

from .DB import DB
from .config import Config

def pair_entries(args):
    '''
    The top level function, called from main when the command 
    is "pair".  

    Arguments:
        args: Namespace object with command line arguments.
    '''
    logging.info(f'Finding matches for unpaired entries')
    logging.debug(f'pair {vars(args)}')

