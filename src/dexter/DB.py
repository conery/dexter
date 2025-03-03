# Database API

import logging

class DB:
    '''
    A collection of static methods that implement the API to
    the database.
    '''

    @staticmethod
    def open(dbname):
        logging.info(f'DB: open {dbname}')
