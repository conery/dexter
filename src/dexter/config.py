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
# The configuration is saved in a class named Config with subclasses
# for commands (Config.import, Config.select, etc)
#

class Config:

    class DB:
        name = 'dexter'
        start_date = '1970-01-01'

    class CSV:
        colmaps = { }
        fullname = { }

def print_default_config():
    '''
    Print a copy of the default config file to the terminal.
    '''
    path = Path(__file__).parent / 'dex.toml'
    with open(path) as f:
        print(f.read())

def inititialize_config(fn = None):
    '''
    Initialize configuration settings.  Looks for a TOML file in
    the following places, in order:
    * the file specified with the --config command line option
    * an environment variable named DEX_CONFIG
    * a file named dex.toml in the current directory
    * a default file in the module's src folder

    After decoding the file save the settings in class variables.

    Arguments:
        fn:  config file name specified on the command line
    '''
    cpath = find_toml_file(fn)
    config = load_toml_file(cpath)

    if dd := config.get('database'):
        if name := dd.get('dbname'):
            Config.DB.name = name
            logging.debug(f'Config.DB.name: {Config.DB.name}')
        if date := dd.get('start_date'):
            Config.DB.start_date = date
            logging.debug(f'Config.DB.start_date: {Config.DB.start_date}')

    if cd := config.get('csv'):
        logging.debug(f'cd {cd}')
        for fmt, spec in cd.items():
            compile_specs(fmt, spec)
            logging.debug(f'Config: parser for {fmt}: {spec}')

###
#
# Helper functions for initialize_config
#

def find_toml_file(fn):
    '''
    Helper function for initialize_config.  Looks for the config file
    in known locations, raises an exception if no config file found.
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

def load_toml_file(fn):
    '''
    Helper function for initialize_config.  Reads the contents of the config
    file, returns a dict with config settings.
    '''
    logging.debug(f'config: reading configuration from {fn}')
    with open(fn, 'rb') as f:
        res = tomllib.load(f)
    return res

@staticmethod
def compile_specs(fmt, specs):
    '''
    Helper method for initialize_config.  Convert column mapping specs into
    Python functions that can be called by the parser.
    '''
    Config.CSV.colmaps[fmt] = { }
    for field, expr in specs.items():
        e = f'lambda rec: {expr}'
        f = eval(e, locals={}, globals={})
        Config.CSV.colmaps[fmt][field] = f

