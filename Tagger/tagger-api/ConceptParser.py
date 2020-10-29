import os
import sys
import struct
import re
from unitex.io import UnitexFile, rm, exists, ls, cp
from unitex.tools import locate, dico, concord
from DictionaryParser import DictionaryParser

# Constants reflecting project file layout, please update if you change where files are stored.
RESOURCES_FILE_PATH = 'resources'
TEMPORARY_FOLDER_PATH = os.path.join(RESOURCES_FILE_PATH, 'Temporary')
# Path to binary file used in batch processing of EHRs
TEMPORARY_FILE_PATH = os.path.join(TEMPORARY_FOLDER_PATH, 'temp.cod')

class ConceptParser:
    ''' Given text, grammar, dictionaries, and a parsing function, will extract
        concepts from text, and return concepts in a dictionary object '''

    # List of all ConceptParser member variables:
    # directory: path of directory holding Unitex files for current parse job
    # options: dictionary holding options for Unitex functions
    # text: path of the text needing concept extraction
    # alphabet_unsorted: path of the alphabet being used, unsorted
    # alphabet_sorted: path of the alphabet being used, sorted
    # grammar: path of the grammar to apply to text
    # dictionaries: list of paths to dictionaries to apply to text
    # parsing_function: input as name of parsing function to use, changed to function pointer to function of same name
    # batch_type: string denoting the size of query being processed, controls which files are cleaned up
    # index: file path of the index created by ConceptParser.locate_grammar()
    # tokens_in_text: list of unique tokens found in the text
    # indices_of_tokens_in_text: list of indices of tokens in the lext, in the order of text itself

    def __init__(self, **kwargs):
        # Update object member variable with passed in arguments.
        self.__dict__.update(kwargs)

        self.index = ''

    def setup(self):
        ''' Initalize attributes that may not be created during __init__ '''
        try:
            # Change function name string to function pointer
            self.parsing_function = ConceptParser.__dict__[self.parsing_function]
        except AttributeError:
            sys.stderr.write('ConceptParser.setup requires ConceptParser.parsing_function attribute to be set')

    def parse(self):
        ''' Apply given dictionaries, grammar, and parsing function to text. Return dictionary of found concepts. '''

        # Create an index (File with locations of strings matching grammar)
        self.index = self.locate_grammar()

        # Build concordance (File with actual strings matching grammar)
        self.build_concordance()

        # Get words that are both in text and dictionary
        # dlf file holds dictionary of simple words that are in dictionaries
        single_words = os.path.join(self.directory, "dlf")
        # dlc file holds dictionary of compound words that are in dictionaries
        multiple_words = os.path.join(self.directory, "dlc")

        # Parse all entities that matched in any dictionary
        dictionary_parser = DictionaryParser(self.get_text(single_words), self.get_text(multiple_words))

        # Get contexts
        contexts_text_path = os.path.join(self.directory, "concord.txt")
        contexts_text = self.get_text(contexts_text_path)

        # If a large batch, we have been given all texts combined toegether
        # We need to separate them and process them individually.
        parsed_concepts = []
        if self.batch_type == 'LARGE_BATCH':
            # Get the tokens that comprise the text
            tokens_in_text_path = os.path.join(self.directory, "tokens.txt")
            self.tokens_in_text = self.get_text(tokens_in_text_path)[1:]

            # Get indices of tokens that comprise the text
            self.indices_of_tokens_in_text = self.get_indices()

            # Get the indices of contexts in the text
            contexts_indices_path = os.path.join(self.directory, "concord.ind")
            contexts_indices = self.get_text(contexts_indices_path )

            # Separate contexts of EHRs into separate lists
            separated_contexts = self.separate_contexts(contexts_text, contexts_indices)

            for separate_context in separated_contexts:
                single_parsed_concept = self.parsing_function(self, separate_context, dictionary_parser)
                parsed_concepts.append([single_parsed_concept])

        # If not a large batch, it is instead a small batch, and we don't need to separate EHRs
        else:
            # Use parsing function specific to this grammar
            parsed_concepts = self.parsing_function(self, contexts_text, dictionary_parser)

        # Cleanup un-needed files to save space
        for file in ls(self.directory):
            # Get file name separate from directory name
            _, file_name = os.path.split(file)
            # Delete all files if a large batch query. Small batches are handled
            #    in 'small_processing' in 'ehrp_utils.py'
            if self.batch_type == 'LARGE_BATCH':
                rm(file)

        # NOTE: parsed_concepts has specific format:
        #   {
        #        name: '<name>',
        #        instances: [
        #            {
        #                <nameOfAttribute1>: '<value>',
        #                <nameOfAttribute2>: '<value>',
        #                ...
        #                <nameOfLastAttribute>: '<value>'
        #            },
        #            ...
        #        ]
        #    }
        return parsed_concepts


    def locate_grammar(self):
        ''' Return index file path, holding locations of matching instances of grammar in text. '''
        # Locate patterns that match grammar
        grammar_applied_successfully = locate(self.grammar, self.text, self.alphabet_unsorted, **self.options['tools']['locate'])

        # Locate created concord.ind file
        index = os.path.join(self.directory, "concord.ind")

        # If application failed or couldn't find associated file
        # if grammar_applied_successfully is False or exists(index) is None:
        if grammar_applied_successfully is False:
            sys.stderr.write("[ERROR] Locate failed!\n")

        return index

    def build_concordance(self):
        ''' Create concord file that holds actual text matching grammar in text file. '''

        concordance_built_successfully = concord(self.index, self.alphabet_sorted, **self.options["tools"]["concord"])
        if concordance_built_successfully is False:
            sys.stderr.write("[ERROR] Concord failed!\n")
            sys.exit(1)

    def get_text(self, file_path):
        '''Get text contents from a file'''
        if exists(file_path) is False:
            sys.stderr.write("[ERROR] File {} not found\n".format(file_path))
        unfile = UnitexFile()
        unfile.open(file_path, mode='r')
        unfile_txt = unfile.read()
        unfile.close()
        return unfile_txt.splitlines()

    def get_indices(self):
        ''' Return the list of indices of tokens that comprise the text '''
        # Get file path for binary file 'text.cod'
        indices_of_tokens_in_text_path = os.path.join(self.directory, "text.cod")

        # Save binary file to local filesystem
        cp(indices_of_tokens_in_text_path, TEMPORARY_FILE_PATH)

        # Open and read binary file
        cod_file = open(TEMPORARY_FILE_PATH, 'rb')
        lines = cod_file.read()

        # We don't delete the temporary file, we just let it get
        #   over-written by following queries

        # Convert bytes to integers
        indices_tuple = struct.unpack("i" * (len(lines) // 4), lines)

        # Convert tuple to list
        indices_list = list(indices_tuple)

        return indices_list

    def make_concepts_object(self, name):
        return {'name': name, 'instances': []}

    def separate_contexts(self, contexts_text, contexts_indices):
        ''' Separate contexts into seprate lists per EHR '''
        separated_contexts = []
        previous_ehr_end = 0

        # Remove metadata at beginning of list
        contexts_indices = contexts_indices[1:]

        # Go through indices of found contexts,
        # When we find a delimiter, clean the surrounding contexts
        for index_number, unitex_index in enumerate(contexts_indices):
            # Now we need to clean the contexts so far
            if '__EHR_API_DELIMITER__' in unitex_index:
                # Keep track of the line separating the EHRs
                most_recent_delimiter = index_number

                # Make sure contexts before delimiter don't include the delimiter text
                self.clean_contexts_before_delimiter(contexts_indices, contexts_text, index_number, unitex_index)

                # Make sure contexts after delimiter don't include the delimiter text
                self.clean_contexts_after_delimiter(contexts_indices, contexts_text, index_number, unitex_index)

                # Save the cleaned contexts before the delimiter as an EHR
                separated_contexts.append(contexts_text[previous_ehr_end:index_number])

                # We add one so that we skip the deliminating context
                previous_ehr_end = index_number + 1

        # Add on last EHR
        separated_contexts.append(contexts_text[most_recent_delimiter+1:])
        return separated_contexts

    def clean_contexts_before_delimiter(self, contexts_indices, contexts_text, index_of_delimiter, delimiter_token_start_and_end):
        ''' Remove any trace of delimiter text in contexts before the delimiter '''

        # Get the token number of where the delimiter starts
        delimiter_token_start = self.get_token_number(delimiter_token_start_and_end, 'START')
        # Get the index of the context we're checking
        index_of_context_to_check = index_of_delimiter - 1

        # Check if at beginning of list
        if index_of_context_to_check < 0:
            return

        # Get the token number of where the right context starts
        context_to_check_token = self.get_token_number(contexts_indices[index_of_context_to_check], 'END') + 1

        # Keep checking and cleaning contexts until we find one that was already clean
        while(self.context_was_cleaned(contexts_text, index_of_context_to_check, delimiter_token_start, context_to_check_token, 'LEFT')):
            index_of_context_to_check -= 1
            try:
                context_to_check_token = self.get_token_number(contexts_indices[index_of_context_to_check], 'END') + 1
            except IndexError:
                break

        return

    def clean_contexts_after_delimiter(self, contexts_indices, contexts_text, index_of_delimiter, delimiter_token_start_and_end):
        ''' Remove any trace of delimiter text in contexts after the delimiter '''

        # Get the token number of where the delimiter starts
        delimiter_token_start = self.get_token_number(delimiter_token_start_and_end, 'START')
        # Get the index of the context we're checking
        index_of_context_to_check = index_of_delimiter + 1
        # Get the token number of where the left context starts
        try:
            context_to_check_token = self.get_token_number(contexts_indices[index_of_context_to_check], 'START') - 1
        # Error occurs if at end of the list
        except IndexError:
            return

        # Keep checking and cleaning contexts until we find one that was already clean
        while(self.context_was_cleaned(contexts_text, index_of_context_to_check, delimiter_token_start, context_to_check_token, 'RIGHT')):
            index_of_context_to_check += 1
            try:
                context_to_check_token = self.get_token_number(contexts_indices[index_of_context_to_check], 'START') + 1
            except IndexError:
                break

        return

    def get_token_number(self, token_string, desired_part):
        ''' Extracts the start or stop token from a given line of the concord.ind file '''
        parts = token_string.split(' ')
        token = parts[0] if desired_part == 'START' else parts[1]
        token_num, char_offset, _ = token.split('.')
        return int(token_num)

    def context_was_cleaned(self, contexts_text, index_of_context_to_check, delimiter_token, context_to_check_token, direction):
        ''' If given context contains part of delimiter, remove delimiter from context and return True, else False'''
        left_context_to_check, term, right_context_to_check = contexts_text[index_of_context_to_check].split('\t')

        # Assume we are moving to the right, and need to look at the left context
        context = left_context_to_check
        offset = -1
        # If we are moving to the left, we need to look at the right context
        if direction == 'LEFT':
            context = right_context_to_check
            offset = 1

        # Set up variables necessay to loop through tokens
        length_of_context = len(context)
        sum_of_chars_per_token = 0
        # Start the tokens at beginning/end of context to check
        next_token_index = context_to_check_token

        # Loop through tokens in context, take action if it overlaps with delimiter
        while sum_of_chars_per_token < length_of_context:
            # If we overlap with the delimiter
            if next_token_index == delimiter_token:
                if direction == 'LEFT':
                    # Take everything up until the start of the delimiter
                    context = context[:sum_of_chars_per_token]
                    context = '\t'.join([left_context_to_check, term, context])
                else:
                    # Take everything starting after the delimiter
                    context = context[length_of_context-sum_of_chars_per_token:]
                    context = '\t'.join([context, term, right_context_to_check])
                break

            # Otherwise, just get next token in the sequence
            # Get the index of which token comes next
            curr_token_index = self.indices_of_tokens_in_text[next_token_index]
            # Get that next token
            curr_token = self.tokens_in_text[curr_token_index]

            # Sum up the length of the token
            sum_of_chars_per_token += len(curr_token)

            # Now use the next token in the context
            next_token_index = next_token_index + offset

        # Runs when we do not break the loop, meaning context did not overlap
        #   with delimiter
        else:
            # False indicates we did not have to clean the context
            return False

        # Update context with cleaned context
        contexts_text[index_of_context_to_check] = context

        # True indicates that yes, we did clean the context
        return True

# -------------- DEFINE PARSING FUNCTIONS BELOW ----------------
# Each parsing function must return concepts like so:
#   {
#        name: '<name>',
#        instances: [
#            {
#                <nameOfAttribute1>: '<value>',
#                <nameOfAttribute2>: '<value>',
#                ...
#                <nameOfLastAttribute>: '<value>'
#            },
#            ...
#        ]
#    }
# Dictionary has one 'name' attribute and an 'instances' attribute that holds a
#   list of found concepts.
#   'name' is used for variable references, should be one word.
#   Each instance in instances is a dictionary of desired attributes and values.
#   Each instance has the same set of attributes, but of course different values.
#
# The id_dict and onto_dict dictionaries are dictionaries that associate concepts
#   to their IDs and the ontology that ID comes from. Each key is in all lowercase
#   letters.

    # masterParser is exception to schema of returned dictionaries
    # It returns a list of dictionaries, each dictionary made by a different parsing function
    # There is a try/except block in extract_concepts to handle this case.
    def masterParser(self, contexts, dictionary_parser):
        used_concepts = {}
        parsed_concepts = []

        # Separate contexts by the parsing function they specify
        for context in contexts:
            left_context, output, right_context = context.split('\t')
            to_parse, parsing_function = output.split('__ParsingFunction__')
            to_parse = left_context + '\t' + to_parse + '\t' + right_context

            # If haven't seen parsing_function yet, add it
            if not(used_concepts.get(parsing_function, False)):
                used_concepts[parsing_function] = [to_parse]
            # Otherwise, add to_parse to parsing function's list
            else:
                used_concepts[parsing_function].append(to_parse)

        # Apply appropriate parsing function to list of contexts
        for parsing_function_str, context_list in used_concepts.items():
            parsing_function = ConceptParser.__dict__[parsing_function_str]
            concepts = parsing_function(self, context_list, dictionary_parser)
            parsed_concepts.append(concepts)

        return parsed_concepts

    # {
    #     name: lookup,
    #     instances: [
    #         {
    #             term: '',
    #             cui: '',
    #             onto: '',
    #         }
    #     ]
    # }
    def lookupParser(self, contexts, dictionary_parser):
        concepts = self.make_concepts_object('lookup');

        # What the user provided
        raw_term = contexts[0].strip()

        # Used to match against dictionaries
        term = raw_term.lower()

        # Find term in dictionaries
        cui, onto = dictionary_parser.get_entry(term, 'lookup', raw_term)

        # Save term if found
        if cui:
            concepts['instances'].append({
                'term': raw_term,
                'cui': cui,
                'onto': onto
            })

        return concepts


    # {
    #     name: drug,
    #     instances: [
    #         {
    #             term: '',
    #             cui: '',
    #             onto: '',
    #             context: '',
    #         }
    #     ]
    # }
    def drugParser(self, contexts, dictionary_parser):
        concepts = self.make_concepts_object('drug');

        # These strings surround each instance of a drug in the found term
        drug_start_delimiter = '__DRUG_START__'
        drug_end_delimiter = '__DRUG_END__'

        drug_start_offset = len(drug_start_delimiter)
        drug_end_offset = len(drug_end_delimiter)

        # Look at each context
        for context in contexts:
            # Split the context into the left/right contexts, and the term that was found
            parts = context.split('\t')
            term = parts[1]

            cleaned_term = term.replace(drug_start_delimiter, '')
            cleaned_term = cleaned_term.replace(drug_end_delimiter, '')

            context = parts[0] + cleaned_term + parts[2]
            context = context.strip()

            # Get first instance of the drug_start_delimiter
            drug_start = term.find(drug_start_delimiter)
            # While we can find drug_start_delimiter, get the paired drug_end_delimiter.
            #   Use these indices to get the drug between them, and update the term,
            #   removing the drug from term.
            while drug_start > -1:
                # Get paired drug_end_delimiter
                drug_end = term.find(drug_end_delimiter)

                # Get drug
                drug = term[drug_start + drug_start_offset:drug_end]
                drug = drug.strip()

                # Remove drug from term
                term = term[drug_end + drug_end_offset:]

                # Lookup cui and onto for this drug
                cui, onto = dictionary_parser.get_entry(drug, 'Drug', context)

                # Cuis is None if drug is a homonym and is not a Drug in this context,
                #   but is instead a different category (Disorder, Procedure, Device)
                if cui:
                    concepts['instances'].append({
                        'term': cleaned_term,
                        'cui': cui,
                        'onto': onto,
                        'context': context
                    })

                drug_start = term.find(drug_start_delimiter)

        return concepts

    # {
    #     name: disorder,
    #     instances: [
    #         {
    #             term: '',
    #             cui: '',
    #             onto: '',
    #             context: ''
    #         }
    #     ]
    # }
    def disorderParser(self, contexts, dictionary_parser):
        concepts = self.make_concepts_object('disorder');

        # These strings surround each instance of a disorder in the found term
        disorder_start_delimiter = '__DISORDER_START__'
        disorder_end_delimiter = '__DISORDER_END__'

        disorder_start_offset = len(disorder_start_delimiter)
        disorder_end_offset = len(disorder_end_delimiter)

        # Look at each context
        for context in contexts:
            # Split the context into the left/right contexts, and the term that was found
            parts = context.split('\t')
            term = parts[1]

            cleaned_term = term.replace(disorder_start_delimiter, '')
            cleaned_term = cleaned_term.replace(disorder_end_delimiter, '')

            context = parts[0] + cleaned_term + parts[2]
            context = context.strip()

            # Get first instance of the disorder_start_delimiter
            disorder_start = term.find(disorder_start_delimiter)
            # While we can find disorder_start_delimiter, get the paired disorder_end_delimiter.
            #   Use these indices to get the disorder between them, and update the term,
            #   removing the disorder from term.
            while disorder_start > -1:
                # Get paired disorder_end_delimiter
                disorder_end = term.find(disorder_end_delimiter)

                # Get disorder
                disorder = term[disorder_start + disorder_start_offset:disorder_end]
                disorder = disorder.strip()

                # Remove disorder from term
                term = term[disorder_end + disorder_end_offset:]

                # Lookup cui and onto for this disorder
                cui, onto = dictionary_parser.get_entry(disorder, 'Disorder', context)

                # Cuis is None if disorder is a homonym and is not a Disorder in this context,
                #   but is instead a different category (Drug, Procedure, Device)
                if cui:
                    concepts['instances'].append({
                        'term': cleaned_term,
                        'cui': cui,
                        'onto': onto,
                        'context': context
                    })

                disorder_start = term.find(disorder_start_delimiter)
        return concepts

    # {
    #     name: device,
    #     instances: [
    #         {
    #             term: '',
    #             cui: '',
    #             onto: '',
    #             context: ''
    #         }
    #     ]
    # }
    def deviceParser(self, contexts, dictionary_parser):
        concepts = self.make_concepts_object('device');

        for context in contexts:
            parts = context.split('\t')
            term = parts[1]
            context = parts[0] + term + parts[2]
            context = context.strip()

            cui, onto = dictionary_parser.get_entry(term, 'Device', context)

            # Save concept if found in dictionary
            if cui:
                concepts['instances'].append({
                    'term': term,
                    'cui': cui,
                    'onto': onto,
                    'context': context
                })

        return concepts

    # {
    #     name: procedure,
    #     instances: [
    #         {
    #             term: '',
    #             cui: '',
    #             onto: '',
    #             context: ''
    #         }
    #     ]
    # }
    def procedureParser(self, contexts, dictionary_parser):
        concepts = self.make_concepts_object('procedure');

        for context in contexts:
            parts = context.split('\t')
            term = parts[1]
            context = parts[0] + term + parts[2]
            context = context.strip()

            cui, onto = dictionary_parser.get_entry(term, 'Procedure', context)

            # Save concept if found in dictionary
            if cui:
                concepts['instances'].append({
                    'term': term,
                    'cui': cui,
                    'onto': onto,
                    'context': context
                })

        return concepts
