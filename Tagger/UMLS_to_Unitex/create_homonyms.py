import re
import sys
import gc
from utility import get_category, unescaped_split, make_output_files

def create_homonyms(input_path, output_folder):
    print('Creating homonym entries...')
    input_file = open(input_path, 'r')
    output_files = make_output_files(output_folder)

    # Used to detect homonyms
    term_cache = {}

    # Create a cache of each term in the input file,
    #   grouping homonyms together
    for count, line in enumerate(input_file):
        if count % 500000 == 0:
            print('On line', count)

        # Get information from current line
        term, cui, onto, types = evaluate(line)
        line_category = get_category(types)

        # Get info about previously found instance of term, if there is one
        duplicate_term = term_cache.get(term)

        # If we've seen this term before
        if duplicate_term:

            # If we haven't seen this cui associated with this term before
            if not(instances_contain(duplicate_term, 'cui', cui)):
                new_instance = term_instance(cui, onto, types)
                duplicate_term.append(new_instance)

            # If this is a duplicate term, but refers to the same cui as already seen term
            else:
                continue

        # If this is the first time encountering this term
        else:
            term_cache[term] = [ term_instance(cui, onto, types) ]

    input_file.close()

    # Combine terms if necessary, and output terms to appropriate file
    combine_entries(term_cache, output_files)

def combine_entries(term_cache, output_files):
    # Now we look at cache of all relavent terms, and group homonyms into
    #   unitex entry lines, 1 per category they fit into.
    # We create unitex entries for non-homonyms as well.
    print('Combining homonym entries...')
    homonyms = ''
    for term, term_info in term_cache.items():
        # Make information per term, per category that term fits into

        # If multiple instances of one term, term is a homonym
        if len(term_info) > 1:
            category_cache = {}

            # Look at each instance of a term
            for instance in term_info:

                # Get that instances category
                instance_category = get_category(instance['types'])

                # Get the catgory dictionary that holds all instances of the same category for this term
                combined_instances_in_category = category_cache.get(instance_category)

                # If instance is of the same category as previously seen instances
                if combined_instances_in_category:
                    # Try to share this instances onto with onto of other instances,
                    #   if other instances have same onto as this instance
                    try:
                        combined_instances_in_category['cuis_and_ontos'][instance['onto']].append(instance['cui'])
                    # If this instance is the first one to use 'onto'
                    except KeyError:
                        combined_instances_in_category['cuis_and_ontos'][instance['onto']] = [instance['cui']]

                    # Union this instances types with other instances types of same category
                    for type in instance['types']:
                        combined_instances_in_category['types'].add(type)

                # If instance is first one of a category
                else:
                    category_cache[instance_category] = {
                        'cuis_and_ontos': {
                            instance['onto']: [instance['cui']]
                        },
                        'types': set(instance['types'])
                    }

            # Format into unitex entries
            unitex_entries = format_homonym(category_cache, term)

            for entry in unitex_entries:
                output_file = get_output_file(entry, output_files)
                output_file.write(entry + '\n')
        # If term is not a homonym, put into unitex format and write to file
        else:
            term_info = term_info[0]
            category = get_category(term_info['types'])
            unitex_entry = '{},{}.{}+{}+{}'.format(term, term_info['cui'], category, term_info['onto'], '+'.join(term_info['types']))
            unitex_entry = unitex_entry.replace('\n', '')
            output_file = get_output_file(unitex_entry, output_files)
            output_file.write(unitex_entry + '\n')

    # Close all files
    for file in output_files.values():
        file.close()

def get_output_file(entry, output_files):
    term, info = unescaped_split(',', entry)
    lemma, types = unescaped_split('\\.', info)
    types = unescaped_split('\\+', types)
    category = types[0]

    return output_files[category]

def format_homonym(category_cache, term):
    homonyms = []
    # Create unitex entry per category term fits into
    for category, category_info in category_cache.items():
        formatted_cuis_and_onto = []
        for onto, cuis in category_info['cuis_and_ontos'].items():
            combined_cuis = '+'.join(cuis)
            # Place CUIs before onto they come from
            formatted_cuis_and_onto.append('{}+{}'.format(combined_cuis, onto))

        # This is our string of cuis and ontologies
        formatted_cuis_and_ontos = '+'.join(formatted_cuis_and_onto)

        # Join types with a '+' symbol
        tuis, sem_types = separate_tuis(category_info['types'])
        formatted_tuis = '+'.join(tuis)
        formatted_sem_types = '+'.join(sem_types)
        formatted_term_types = '{}+{}'.format(formatted_sem_types, formatted_tuis)

        # Put line in unitex format
        homonym = '{},HOMONYM.{}+{}+{}'.format(term, category, formatted_cuis_and_ontos, formatted_term_types)
        # Really make sure no extra newlines
        homonym = homonym.replace('\n', '')
        homonyms.append(homonym)

    return homonyms

def separate_tuis(types):
    tuis, sem_types = [], []
    for type in types:
        if is_tui(type):
            tuis.append(type)
        else:
            sem_types.append(type)
    return tuis, sem_types

def is_tui(type):
    # TUIs start with 'T', are of length 4
    if type[0] == 'T' and len(type) == 4:
        # TUIs only contain digits after leading 'T'
        for char in type[1:]:
            try:
                int(char)
            except ValueError:
                break
        # Return True if all characters in type are digits, except for leading 'T'
        else:
            # Is a TUI
            return True

    # Not a TUI
    return False

def term_instance(cui, onto, types):
    new_instance = {
        'cui': cui,
        'onto': onto,
        'types': [type.strip() for type in types]
    }
    return new_instance

def evaluate(line):
    # Get the term we are looking at
    try:
        term, info = unescaped_split(',', line)
    except ValueError as err:
        # Special case, where term ends with a slash
        line = line.replace('18\\,', '18,')
        term, info = unescaped_split(',', line)

    # Get CUI and ontology of term in line
    cui, info = unescaped_split('\\.', info)

    info = unescaped_split('\\+', info)
    onto = info[0]
    types = info[1:]

    return term, cui, onto, types

def instances_contain(instances, field, to_find):
    ''' Determine if 'to_find' already exists in 'field' of each instance '''
    for instance in instances:
        if to_find == instance[field]:
            return True
    return False
