# Flask imports
from flask import jsonify, abort
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage

# User defined imports
from ehrp_utils import extract_concepts

class Ehrs(Resource):
    '''Ehrs endpoint for extracting Biomedical named entities and mapping to their respective concept IDs'''
    def __init__(self, OPTIONS, ALL_GROUPINGS, ALL_DICTS_AND_ONTOLOGIES):
        self.OPTIONS = OPTIONS
        self.ALL_GROUPINGS = ALL_GROUPINGS
        self.ALL_DICTS_AND_ONTOLOGIES = ALL_DICTS_AND_ONTOLOGIES

        # Define allowable arguments
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('text', required=False, default=None, action='append',
                               location=['values', 'json'], help="text for extracting entities and concept ids")
        self.reqparse.add_argument('types', type=str, required=False, default=None, action='append',
                               location=['values', 'json'], help="type of concept to extract")
        self.reqparse.add_argument('file', type=FileStorage, required=False, default=None,
                               location='files', help="optional file to be parsed, at most one of 'text' or 'file' should have data")
        super(Ehrs, self).__init__()

    def post(self):
        '''POST method'''
        # For debugging
        print("POST - Ehrs")

        # Get arguments
        args = self.reqparse.parse_args()
        text = args['text']
        types = args['types']
        file = args['file']

        # If user tries to use 'lookup' graph in extract operation or use 'master' specifically.
        if types and ( ('lookup' in types) or ('master' in types) ):
            print('''[ERROR] User tried to use \'lookup\' in extract operation
                  or specified master graph''')
            abort(422)

        # If both set or neither set
        if (text and file) or not(text or file):
            print('[ERROR] Either both text and file are being used, or neither are')
            abort(422)

        # If file is set, text isn't, and so we update text with the contents of file
        if file:
            # Assume file has one EHR per line
            text = [str(line) for line in file]

        # If no types specified, look for all types
        if types == None:
            concepts = extract_concepts(self.OPTIONS, self.ALL_GROUPINGS, self.ALL_DICTS_AND_ONTOLOGIES, text)
        # Otherwise use the types specified
        else:
            concepts = extract_concepts(self.OPTIONS, self.ALL_GROUPINGS, self.ALL_DICTS_AND_ONTOLOGIES, text, types)

        return jsonify(concepts)

class Terms(Resource):
    '''Terms endpoint for finding the relevant concept ID'''
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('term', type=str, required=True, location='args',
                               help="text for finding concept id")
        super(Terms, self).__init__()

    def get(self):
        '''GET method'''

        # For debugging
        print("GET - Terms")

        # Get argument
        args = self.reqparse.parse_args()

        # Make into a singleton list, as expected by 'extract_concepts'
        term = [args['term']]

        # Get results
        concepts = extract_concepts(OPTIONS, ALL_GROUPINGS, ALL_DICTS_AND_ONTOLOGIES, term, ['lookup'])

        return jsonify(concepts)
