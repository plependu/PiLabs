'''
Utility file containing Unitex related utility methods
'''

from __future__ import print_function
from flask import abort
import os
import sys
import random
import string
import json
from ConceptParser import ConceptParser
from unitex.io import ls, rm, cp, exists, UnitexFile, mv
from unitex.tools import UnitexConstants, normalize, tokenize, dico
from unitex.resources import free_persistent_alphabet, load_persistent_alphabet

# Constants reflecting project file layout, please update if you change where files are stored.
RESOURCES_RELATIVE_PATH = 'resources'
GRAMMAR_RELATIVE_PATH = os.path.join(RESOURCES_RELATIVE_PATH, 'Grammars')
DICTIONARY_RELATIVE_PATH = os.path.join(RESOURCES_RELATIVE_PATH, 'Dictionaries')

# Constants obtained by empirical tests
MEDIUM_CUTOFF = 730

# Called from ehrp_api.py
def load_alphabets(options):
    ''' Place alphabets in persistent space for re-use. '''
    options['resources']['alphabet'] = load_persistent_alphabet(options['resources']['alphabet'])
    options['resources']['alphabet-sorted'] = load_persistent_alphabet(options['resources']['alphabet-sorted'])

# Called from ehrp_api.py
def free_alphabets(options):
    ''' Remove alphabets from persistent space when api is shut down. '''
    free_persistent_alphabet(options['resources']['alphabet'])
    free_persistent_alphabet(options['resources']['alphabet-sorted'])

# Called from ehrp_api.py
def extract_concepts(options, all_groupings, dicts_and_ontos, text, concepts_to_get='ALL'):
    '''
    Extracts concepts from text.
    Returns dictionary of found concepts.
    '''

    print("Extracting concepts from text . . .")

    # Load chosen dict and grammar groupings from all_groupings
    chosen_groupings = get_concepts_from_groupings(all_groupings, concepts_to_get)

    # Get Alphabets
    alphabet_unsorted = options["resources"]["alphabet"]
    alphabet_sorted = options["resources"]["alphabet-sorted"]

    # Get list of dictionary files to be used
    dictionaries = dicts_and_ontos['dictionaries']

    # Get how many texts we need to process
    num_texts_to_process = len(text)

    # List to store extracted concepts per EHR
    concepts_per_ehr = []

    # Choose most efficient option for processing texts

    # Option 1: Apply dictionaries to combined texts, and share resultant files between each text
    if num_texts_to_process <= MEDIUM_CUTOFF:
        # Get the concepts from each text
        concepts_per_ehr = medium_processing(text, alphabet_unsorted, alphabet_sorted, dictionaries, chosen_groupings, options)

    # Option 2: For large batches, combine texts and process all together, then separate out results
    else:
        concepts_per_ehr = batch_processing(text, alphabet_unsorted, alphabet_sorted, dictionaries, chosen_groupings, options)

    # If only given one EHR, change singleton list to single object
    if num_texts_to_process == 1:
        concepts_per_ehr = concepts_per_ehr[0]

    # Clean up the created Unitex files
    print("Cleaning up files")
    for v_file in ls("%s" % UnitexConstants.VFS_PREFIX):
        rm(v_file)

    return concepts_per_ehr

# Function: get_concepts_from_groupings; Return only those grammar/function pairs specified in the query
# all_groupings: List of dictionary groupings of grammar/function pairs
def get_concepts_from_groupings(all_groupings, concepts_to_get):
    ''' Returns list of concepts to get as specified by user '''
    concepts = []

    # If all concepts desired, use master graph and any sub-graphs not included in master graph.
    # This is faster than making many individual queries.
    if concepts_to_get == 'ALL':
        for grouping in all_groupings:
            if grouping['grammar'] == 'master.fst2':
                concepts.append(grouping)
                return concepts

    # If specific concepts are desired
    for concept in concepts_to_get:
        # Match desired concepts with associated grouping
        for grouping in all_groupings:
            # Accepted concept types are specified in GrammarParsingFunction.json
            if grouping['grammar'] == concept + '.fst2':
                concepts.append(grouping)
                break
        # If concept not found, must be incorrectly specified, so abort
        else:
            incorrect_concept_type(concept)
    return concepts

# Function: pre_process_texts: Normalize and tokenize each given text
# texts: list of strings to be processed
def pre_process_texts(texts, alphabet_unsorted, options):
    health_record_paths = []
    for record_number, health_record in enumerate(texts):
        # Create file name that will hold content
        health_record_file_name = to_VFS("text_%d" % record_number)

        # Place file into VFS
        health_record_path = health_record_file_name + ".txt"

        # Save content in Unitex file
        save_to_unitex_file(health_record_path, health_record)

        # Pre-process this file to allow for later processing
        normalize_text(health_record_path, options["tools"]["normalize"])
        health_record_processed_text_path = health_record_file_name + ".snt"
        # Save processed file path for later processing
        health_record_paths.append(health_record_processed_text_path)
        tokenize_text(health_record_processed_text_path, alphabet_unsorted, options["tools"]["tokenize"])

    # List of paths for each file needing to be further processed
    return health_record_paths

# Function: apply_dictionaries; Applies dictionaries to text, finding the overlap between them
# dictionaries: List of file paths to the dictionaries to be used
# text: File path to the text to be processed
# alphabet_unsorted: File path to the alphabet to be used, unsorted
# options: Dictionary of options for use with unitex functions
def apply_dictionaries(dictionaries, text, alphabet_unsorted, options):
    ''' Creates .dlf and .dlc files holding words in both dictionaries and text. '''
    if dictionaries is not None:
        dictionaries_applied_succesfully = dico(dictionaries, text, alphabet_unsorted, **options['tools']['dico'])

        if dictionaries_applied_succesfully is False:
            sys.stderr.write("[ERROR] Dictionaries application failed!\n")
            sys.exit(1)
    else:
        sys.stderr.write("[ERROR] No dictionaries specified.\n")

# Function: to_VFS; Prepend the Unitex VFS prefix to given file path
def to_VFS(file_path):
    return "%s%s" % (UnitexConstants.VFS_PREFIX, file_path)

# function: get_concepts_for_grammars; Returns a list of dictionary objects of parsed concepts from text
# directory: virtual file system directory
# options: yaml object with preset options for different unitex functions
# snt: the file path to the pre-processed text
# alphabet_unsorted: file path to alphabet unitex should use, unsorted
# alphabet_sorted: file path to alphabet unitex should use, sorted
# chosen_groupings: The groupings from GrammarParsingFunction.json that will be applied to the input text
# batch_type: string denoting the size of the query being processed
def get_concepts_for_grammars(directory, options, snt, alphabet_unsorted, alphabet_sorted, chosen_groupings, batch_type):
    list_of_concepts = []

    # Set arguments that don't change across grammar/dictionary usage
    concept_parser = ConceptParser(
        directory = directory,
        options = options,
        text = snt,
        alphabet_unsorted = alphabet_unsorted,
        alphabet_sorted = alphabet_sorted,
        batch_type = batch_type
    )

    # Set concept_parser grammar, dictionaries, and parsing_functions to those in GrammarDictionaryParsingFunction.py
    for grammar_dictionary_parser in chosen_groupings:
        grammar_path = os.path.join(GRAMMAR_RELATIVE_PATH, grammar_dictionary_parser['grammar'])

        concept_parser.grammar = grammar_path
        concept_parser.parsing_function = grammar_dictionary_parser['parsing_function']

        # Make use of ConceptParser member variables that might not be set during object construction
        # Maps parsing_function string to function reference
        concept_parser.setup()

        # Process snt using concept_parser.grammar, concept_parser.dictionaries, and concept_parser.parsing_function
        concepts = concept_parser.parse()

        try:
            # Append only if at least one concept found.
            if len(concepts['instances']):
                list_of_concepts.append(concepts)
        # This happens if we are parsing the master graph
        except TypeError:
            list_of_concepts.extend(concepts)

    return list_of_concepts

# Function: medium_processing; Processes each text provided, and returns a list of concepts extracted from each one
# text: list of strings to be processed, each string is one health record
# alphabet_unsorted: file path to the alphabet to be used, unsorted
# alphabet_sorted: file path to the alphabet to be used, sorted
# dictionaries: list of file paths to dictionaries to be used
# chosen_groupings: the list of grammars and associated parsing functions to be applied to each text
# options: dictionary of options for various unitex funtions
def medium_processing(text, alphabet_unsorted, alphabet_sorted, dictionaries, chosen_groupings, options):
    ''' Handles queries with small number of documents. '''
    # Put all texts together for preprocessing
    combined_text = '\n\n'.join(text)

    # Create folder in virtual file system
    combined_text_filename = to_VFS(random_filename())
    combined_text_path = combined_text_filename + ".txt"

    # Save combined text in file in VFS
    save_to_unitex_file(combined_text_path, combined_text)

    # Normalize the combined text, creates a 'combined_text_filename.snt' file
    normalize_text(combined_text_path, options["tools"]["normalize"])

    # Get file path of normalized text
    combined_processed_text_path = combined_text_filename + ".snt"

    # Tokenize the text (alters combined_processed_text in place)
    tokenize_text(combined_processed_text_path, alphabet_unsorted, options["tools"]["tokenize"])

    # Apply dictionaries
    apply_dictionaries(dictionaries, combined_processed_text_path, alphabet_unsorted, options)

    # Create a text file in the VFS for each health record
    health_record_paths = pre_process_texts(text, alphabet_unsorted, options)

    # Get concepts that match grammars
    concepts_per_ehrp = []
    prev_dic_files_locations = {
        "dlf": os.path.join(combined_text_filename + "_snt", "dlf"),
        "dlc": os.path.join(combined_text_filename + "_snt", "dlc")
    }
    for record_number, health_record_path in enumerate(health_record_paths):
        # Get the folder in which all files for this health record are stored
        health_record_folder = to_VFS("text_%d_snt" % record_number)
        # Need to place dictionary files into this folder, set up paths to do so
        new_dlf_path = os.path.join(health_record_folder, "dlf")
        new_dlc_path = os.path.join(health_record_folder, "dlc")

        # Place the dictionary files into this folder
        mv(prev_dic_files_locations["dlf"], new_dlf_path)
        mv(prev_dic_files_locations["dlc"], new_dlc_path)

        # Update location of dictionay files
        prev_dic_files_locations["dlf"] = new_dlf_path
        prev_dic_files_locations["dlc"] = new_dlc_path

        # Apply graphs to text and get found concepts
        concepts = get_concepts_for_grammars(health_record_folder, options, health_record_path,
                                            alphabet_unsorted, alphabet_sorted,
                                            chosen_groupings, 'MEDIUM_BATCH'
                                            )

        # Remove unnecessary files to save space
        remove_files(health_record_folder, exceptions=['dlf', 'dlc'])

        concepts_per_ehrp.append(concepts)
    return concepts_per_ehrp

# Function: batch_processing; Processes each text provided, and returns a list of concepts extracted from each one
# text: list of strings to be processed, each string is one health record
# alphabet_unsorted: file path to the alphabet to be used, unsorted
# alphabet_sorted: file path to the alphabet to be used, sorted
# dictionaries: list of file paths to dictionaries to be used
# chosen_groupings: the list of grammars and associated parsing functions to be applied to each text
# options: dictionary of options for various unitex funtions
def batch_processing(text, alphabet_unsorted, alphabet_sorted, dictionaries, chosen_groupings, options):
    ''' Handles queries with large number of documents. '''
    # Put all texts together for preprocessing
    combined_text = '__EHR_API_DELIMITER__'.join(text)
    combined_text_filename = to_VFS(random_filename())
    combined_text_path = combined_text_filename + '.txt'

    # Place combined text into Unitex file
    save_to_unitex_file(combined_text_path, combined_text)

    # Normalize the combined texts
    normalize_text(combined_text_path, options["tools"]["normalize"])

    # Get file path of normalized text
    combined_processed_text_path = combined_text_filename + ".snt"

    # Tokenize the text (alters combined_processed_text in place)
    tokenize_text(combined_processed_text_path, alphabet_unsorted, options["tools"]["tokenize"])

    # Get paths of dlf and dlc files inside designated folder
    dlf_relative_path = os.path.join('Internal_api_use', 'dlf')
    dlc_relative_path = os.path.join('Internal_api_use', 'dlc')

    # Get paths of dlf and dlc files inside the Dictionaries folder
    dlf_path = os.path.join(DICTIONARY_RELATIVE_PATH, dlf_relative_path)
    dlc_path = os.path.join(DICTIONARY_RELATIVE_PATH, dlc_relative_path)

    # Make folder name that holds all relevant files
    folder_name = combined_text_filename + '_snt'
    # Make destination path for dlf and dlc files
    dlf_destination_path = os.path.join(folder_name, 'dlf')
    dlc_destination_path = os.path.join(folder_name, 'dlc')

    # Copy these pre-build dictionaries into VFS
    cp(dlf_path, dlf_destination_path)
    cp(dlc_path, dlc_destination_path)

    concepts_per_ehr = get_concepts_for_grammars(folder_name, options, combined_processed_text_path,
                                                alphabet_unsorted, alphabet_sorted,
                                                chosen_groupings, 'LARGE_BATCH'
                                            )
    return concepts_per_ehr

# Function: save_to_unitex_file; Creates a unitex file at given location with given content
# path: file path inside the unitex VFS
# content: string to be written to file
def save_to_unitex_file(path, content):
    unitex_file = UnitexFile()
    unitex_file.open(path, mode='w')
    unitex_file.write(content)
    unitex_file.close()

def remove_files(directory, exceptions):
    ''' Used to remove files in a given VFS folder '''
    # Join directory name with file names specified in exceptions
    exceptions = [os.path.join(directory, file_name) for file_name in exceptions]

    for file in ls(directory):
        is_exception = file in exceptions
        # Don't delete files specified in exceptions list
        if not(is_exception):
            rm(file)

def get_json_from_file(file_path):
    ''' Loads the user-chosen groupings of grammars, dictionaries, and parsing functions as a dictionary '''
    with open(file_path) as file:
        groupings = json.load(file)
    return groupings

def random_filename(size=8, chars=string.ascii_uppercase + string.digits):
    '''Returns a random string'''
    return ''.join(random.choice(chars) for _ in range(size))

def normalize_text(text, kwargs):
    ''' Creates .snt file of the normalized text '''
    # normalize returns True on succeess, False on failure
    normalization_succeeded = normalize(text, **kwargs)

    if normalization_succeeded is False:
        sys.stderr.write("[ERROR] Text normalization failed!\n")

def tokenize_text(snt_file_path, alphabet, kwargs):
    ''' Creates file of tokens '''
    tokenization_succeeded = tokenize(snt_file_path, alphabet, **kwargs)

    if tokenization_succeeded is False:
        sys.stderr.write("[ERROR] Text tokenization failed!\n")
        sys.exit(1)

# TODO: Raise exception that can be handled, to return a more descriptive error
def incorrect_concept_type(incorrect_type):
    # Unprocessable entity error
    abort(422)

def dict_names_to_paths(dict_names):
    ''' Changes dictionary names to dictionary paths '''
    return [os.path.join(DICTIONARY_RELATIVE_PATH, name) for name in dict_names]
