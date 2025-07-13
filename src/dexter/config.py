#
# Configuration
#
# Read the configuration file, make it accessible as a global
# variable that can be imported by other modules.
#

from collections import namedtuple
from enum import Enum
import logging
import os
from pathlib import Path
import tomllib

###
# 
# A ColMap tuple tells the parser where to find essential
# information in a CSV file
#

ColMap = namedtuple('ColMap', ['description', 'date', 'amount', 'column'])

###
#
# Tags for Trabsaction and Entry objects

class Tag(Enum):
    B = '#budget'
    P = '#pending'
    U = '#unpaired'
    X = '#xfer'

###
# 
# The configuration is saved in a singleton object that provides an
# abstract intertace to configuration settings
#

class Config:
    '''
    A collection of static methods and attributes that implement the 
    API to the config file.
    '''

    path_to_default = Path(__file__).parent / 'dex.toml'

    cname = 'credit'
    dname = 'debit'

    tag_syms = {
        Tag.U: ['⊏', '⊐'],
        Tag.X: ['⊢', '⊣'],
        Tag.P: ['◻︎', '◻︎'],
        Tag.B: ['⊜', '⊜'],
    }

    # parsers = { }
    colmaps = { }
    fullname = { }

    dbname = 'dexter'
    start_date = '1970-01-01'

    @staticmethod
    def print_default():
        with open(Config.path_to_default) as f:
            print(f.read())

    @staticmethod
    def init(cfile: str | None):
        '''
        Initialize configuration settings.  Looks for a TOML file in
        the following places, in order:
        * the file specified with the --config command line option
        * an environment variable named DEX_CONFIG
        * a file named dex.toml in the current directory
        * a default file in the module's src folder

        After decoding the file save the settings in class variables.

        Arguments:
            cfile:  config file name specified on the command line
        '''
        config = Config.load_toml_file(cfile)

        if td := config.get('terminology'):
            Config.dname = td['dname']
            Config.cname = td['cname']
            logging.debug(f'config: cname = "{Config.cname}" dname = "{Config.dname}"')

        if cd := config.get('csv'):
            logging.debug(f'cd {cd}')
            for fmt, spec in cd.items():
                logging.debug(f'fmt {fmt} spec {spec}')
                Config.compile_specs(fmt, spec)

        if dd := config.get('database'):
            Config.dbname = dd.get('dbname')
            Config.start_date = dd.get('start_date')

        # logging.debug(f'config: parsers: {Config.parsers}')
        logging.debug(f'config: dbname: {Config.dbname}')
        logging.debug(f'config: colmaps: {Config.colmaps}')
        logging.debug(f'config: fullname: {Config.fullname}')

    @staticmethod
    def find_toml_file(fn):
        '''
        Helper function for Config.init.  Locate the config
        file to use.  Either raises an exception or returns
        a file path.
        '''
        p = fn or os.getenv('DEX_CONFIG')
        if p is not None:
            config_path = Path(p)
            if not config_path.is_file():
                raise FileNotFoundError(f'init_config: no such file: {config_path}')
            return config_path
        
        config_path = Path.cwd() / 'dex.toml'
        if config_path.is_file():
            return config_path
        
        project_dir = Path(__file__).parent
        config_path = project_dir / 'dex.toml'
        if not config_path.is_file():
            raise ModuleNotFoundError(f'no config file in distribution?')
        return config_path

    @staticmethod
    def load_toml_file(fn):
        '''
        Helper function for Config.init.  Reads the contents of the config
        file, returns a dict with config settings.
        '''
        path = Config.find_toml_file(fn)
        logging.debug(f'config: reading configuration from {path}')
        with open(path, 'rb') as f:
            res = tomllib.load(f)
        return res
    
    @staticmethod
    def compile_specs(fmt, specs):
        '''
        Helper method for Config.init.  Convert column mapping specs into
        Python functions that can be called by the parser.
        '''
        Config.colmaps[fmt] = { }
        for field, expr in specs.items():
            e = f'lambda rec: {expr}'
            f = eval(e, locals={}, globals={})
            Config.colmaps[fmt][field] = f

