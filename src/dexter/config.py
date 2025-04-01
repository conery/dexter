#
# Configuration
#
# Read the configuration file, make it accessible as a global
# variable that can be imported by other modules.
#

from collections import namedtuple
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
# The configuration is saved in a singleton object that provides an
# abstract intertace to configuration settings
#

class Config:
    '''
    A collection of static methods and attributes that implement the 
    API to the config file.
    '''

    cname = 'credit'
    dname = 'debit'

    unpaired_tag = '#unpaired'

    # parsers = { }
    colmaps = { }
    fullname = { }

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

        # logging.debug(f'config: parsers: {Config.parsers}')
        logging.debug(f'config: colmaps: {Config.colmaps}')
        logging.debug(f'config: fullname: {Config.fullname}')

    @staticmethod
    def load_toml_file(fn):
        '''
        Helper function for Config.init.  Locates the config file to
        use, reads the contents, returns a dict with config settings.
        '''
        if fn is not None:
            config_path = Path(fn)
            if not config_path.is_file():
                raise ValueError(f'init_config: no such file: {fn}')
        elif fn := os.getenv('DEX_CONFIG'):
            project_dir = Path(__file__).parent
            config_path = project_dir / 'dex.toml'
            if not config_path.is_file():
                raise ValueError(f'init_config: no such file: {fn}')
        else:
            config_path = Path.cwd() / 'dex.toml'
            if not config_path.is_file():
                config_path = Path(__file__).parent / 'dex.toml'
        logging.debug(f'config: reading {config_path}')

        with open(config_path, 'rb') as f:
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

