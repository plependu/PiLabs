# Flask imports
from flask import Flask
from flask_restful import Api

# Unitex imports
from unitex import init_log_system
from unitex.config import UnitexConfig

# User defined imports
from ehrp_utils import load_alphabets, free_alphabets, get_json_from_file, dict_names_to_paths
from file_paths import RESOURCES_RELATIVE_PATH, GRAMMAR_PARSING_GROUPS_PATH, DICTS_AND_ONTOLOGIES_PATH
from endpoint_resources import Ehrs, Terms

# Miscellaneous
import os
import argparse
import yaml

# Used in user-defined flask-restful resources
OPTIONS = None
ALL_GROUPINGS = None
ALL_DICTS_AND_ONTOLOGIES = None

''' Parses arguments and starts the api '''

# -------------------- Get initial arguments passed in ---------------------

parser = argparse.ArgumentParser()

# Define resource locations
parser.add_argument('--conf', type=str, default=os.path.join(RESOURCES_RELATIVE_PATH, 'unitex-med.yaml'),
                    help="Path to yaml file")

# Define API settings
parser.add_argument('--host', type=str, default='localhost',
                    help="Host name (default: localhost)")
parser.add_argument('--port', type=int, default='8020', help="Port (default: 8020)")

args = parser.parse_args()

#----------------------end argument parsing ------------------------------------


#----------------------- Set up unitex --------------------------------------

# Load resources
config = None
with open(args.conf, "r") as c_file:
    config = yaml.load(c_file)
OPTIONS = UnitexConfig(config)
init_log_system(OPTIONS["verbose"], OPTIONS["debug"], OPTIONS["log"])
load_alphabets(OPTIONS)

# Get all grammar and parsing function groupings
ALL_GROUPINGS = get_json_from_file(GRAMMAR_PARSING_GROUPS_PATH)

# Get all dictionary and ontology names
ALL_DICTS_AND_ONTOLOGIES = get_json_from_file(DICTS_AND_ONTOLOGIES_PATH)
ALL_DICTS_AND_ONTOLOGIES['dictionaries'] = dict_names_to_paths(ALL_DICTS_AND_ONTOLOGIES['dictionaries'])

#------------------------end Unitex setup --------------------------------------


# --------------------------- Start flask app ------------------------------

print("Starting app . . .")
app = Flask(__name__)

# Running DEBUG mode for flask. Makes JSON outputs more readable.
app.config['DEBUG'] = True
api = Api(app, prefix='/ehrp-api/v1')

# Handle missing page 404 error
@app.errorhandler(404)
def page_not_found(error):
    '''Error message for page not found'''
    return "page not found : {}".format(error)

# Handle internal server error
@app.errorhandler(500)
def raise_error(error):
    '''Error message for resource not found'''
    return error

# ================== Define routes to resources ================================
# Define endpoint for the Ehrs resource
resource_args = (OPTIONS, ALL_GROUPINGS, ALL_DICTS_AND_ONTOLOGIES)
api.add_resource(Ehrs, '/ehrs', resource_class_args=resource_args)

# Define endpoint for the Terms resource
api.add_resource(Terms, '/terms', resource_class_args=resource_args)
# ================== End route and resource definitions ========================

# Start the app
app.run(host=args.host, port=args.port)

# Free resources when api closes
free_alphabets(OPTIONS)

#------------------- End flask app startup -------------------------------------
