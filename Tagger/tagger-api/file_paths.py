import os

# Constants reflecting project file layout, please update if you change where files are stored.
RESOURCES_RELATIVE_PATH = 'resources'
GRAMMAR_RELATIVE_PATH = os.path.join(RESOURCES_RELATIVE_PATH, 'Grammars')
DICTIONARY_RELATIVE_PATH = os.path.join(RESOURCES_RELATIVE_PATH, 'Dictionaries')
GRAMMAR_PARSING_GROUPS_PATH = os.path.join(RESOURCES_RELATIVE_PATH, 'GrammarParsingFunction.json')
DICTS_AND_ONTOLOGIES_PATH = os.path.join(RESOURCES_RELATIVE_PATH, 'DictsAndOntologies.json')
