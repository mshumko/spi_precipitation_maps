import warnings
import pathlib
import configparser

__version__ = '0.0.1'

# Load the configuration settings.
here = pathlib.Path(__file__).parent.resolve()
config = {'project_dir':here}

# Not needed for now.
# settings = configparser.ConfigParser()
# settings.read(here / 'config.ini')

# # Go here if config.ini exists (don't crash if the project is not yet configured.)
# if 'Paths' in settings:  
#     try:
#         project_dir = settings['Paths']['project_dir']
#         project_data_dir = settings['Paths']['project_data_dir']
#         config['data_dir'] = project_data_dir
#     except KeyError as err:
#         warnings.warn('The project package did not find the config.ini file. '
#             'Did you run "python3 -m package config"?')