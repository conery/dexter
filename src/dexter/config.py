#
# Configuration
#
# Read the configuration file, make it accessible as a global
# variable that can be imported by other modules.
#

import logging
import os
from pathlib import Path
import tomllib

def init_config(cfile: str | None):
    '''
    Initialize configuration settings.  Looks for a TOML file in
    the following places, in order:
      * the file specified with the --config command line option
      * an environment variable named DEX_CONFIG
      * a file named dex.toml in the current directory
      * a default file in the module's src folder

    Arguments:
        cfile:  config file name specified on the command line
    '''
    if cfile is not None:
        config_path = Path(cfile)
        if not config_path.is_file():
            raise ValueError(f'init_config: no such file: {cfile}')
    elif cfile := os.getenv('DEX_CONFIG'):
        project_dir = Path(__file__).parent
        config_path = project_dir / 'dex.toml'
        if not config_path.is_file():
            raise ValueError(f'init_config: no such file: {cfile}')
    else:
        config_path = Path.cwd() / 'dex.toml'
        if not config_path.is_file():
           config_path = Path(__file__).parent / 'dex.toml'
    logging.debug(f'config file: {config_path}')
