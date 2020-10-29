import re
import sys
import WordSenseDisambiguation as WSD

'''
    Provides the 'get_entry' functionality to get the CUI and ONTO of a term.
'''
class DictionaryParser():
    def __init__(self, simple_words, compound_words):
        self.simple_entities =  simple_words
        self.compound_entities = compound_words
        self.entities = self.simple_entities + self.compound_entities

        # Lookup table of terms found in the text
        self.terms = {}
        self.parse_entities()


    def parse_entities(self):
        ''' Create a lookup table of entities, indexed by term. '''
        for entity in self.entities:
            # Get an Entity object, after parsing Unitex format dictionary entry
            decomposed_entity = self.decompose(entity)

            # The term itself, ex: 'tylenol'
            term = decomposed_entity.term

            # Changed escaped commas and periods to unescaped versions
            term = term.replace('\\,', ',')
            term = term.replace('\\.', '.')

            # List of Instance objects
            instances = decomposed_entity.instances

            # If entity is a homonym, put all instances together
            if decomposed_entity.is_homonym:
                try:
                    self.terms[term].extend(instances)
                except KeyError:
                    self.terms[term] = instances
            # If not a homonym, create entry
            else:
                self.terms[term] = instances


    def get_entry(self, term, category, context):
        ''' Get CUI and ONTO of 'term'. '''
        instances = self.terms.get(term.lower(), None)

        # If not fount (Lookup can cause this), return
        if not(instances):
            return None, None

        # If the term has multiple meanings
        if len(instances) > 1:
            # Decide which meaning is most appropriate, given the context
            instance = WSD.get_meaning(instances, term, context)

            # If most appropriate meaning is the same as current category
            if instance.category == category:
                return instance.cui, instance.onto

            # If most appropriate meaning is different from current category
            else:
                return None, None

        # If term has just one meaning
        else:
            # Set instance to be the only meaning there is
            instance = instances[0]
            return instance.cui, instance.onto

    def decompose(self, entity):
        ''' Break Unitex format entry into a list of Instances. '''

        # Separate term and lemma from the entity
        term, info = unescaped_split(',', entity)
        lemma_end = info.find('.')
        lemma = info[:lemma_end]
        info = info[lemma_end+1:]

        # Boolean indicating if the entity is a homonym or not
        is_homonym = True if lemma == 'HOMONYM' else False

        # Split remaining attributes
        attributes = unescaped_split('\\+', info)

        # First attribute is always category
        category = attributes[0]

        # Remove category from attributes
        attributes = attributes[1:]

        # Aggregate information into 'instances' list
        instances = []

        # If entity has multiple possible meanings
        if is_homonym:
            cuis = []

            # Look at each attribute of the current entry
            for attribute in attributes:
                # While CUIs occur one after another, aggregate them in 'cuis'
                if is_cui(attribute):
                    cuis.append(attribute)
                    last_attribute_was_cui = True

                # If a non-cui attribute follows a cui attribute
                elif last_attribute_was_cui:
                    # Use all cuis seen so far, creating an Instance per cui
                    instances.extend( [Instance(cui, attribute, category) for cui in cuis] )

                    # Reset cuis to be empty
                    cuis = []

                    # Reset boolean
                    last_attribute_was_cui = False

                # If neither a CUI or onto, then we've seen all CUIs and ontos for this entity
                else:
                    break

        # If entity has just one meaning
        else:
            # If entity is not a homonym, onto is the next attribute
            onto = attributes[0]

            # Make a singleton list
            instances = [ Instance(lemma, onto, category) ]

        return Entity(term, is_homonym, instances)

class Entity:
    def __init__(self, term, is_homonym, instances):
        self.term = term
        self.is_homonym = is_homonym
        self.instances = instances

class Instance:
    def __init__(self, cui, onto, category):
        self.cui = cui
        self.onto = onto
        self.category = category

def is_homonym(instances):
    ''' Boolean whether a list of instances is a homonym. '''
    return True if len(instances) > 1 else False

def unescaped_split(delimiter, line):
    ''' Split line on unescaped instances of delimiter. '''
    return re.split(r'(?<!\\){}'.format(delimiter), line)

def is_cui(attribute):
    ''' Given a string attribute, determine if it is a CUI. '''

    # Attribute must exist
    if len(attribute) == 0:
        return False

    # All CUIs start with 'C'
    starts_with_C = attribute[0] == 'C'

    # All CUIs are of total length 8
    length_of_eight = len(attribute) == 8

    # Determine if all characters after the first are able to be cast to integers
    try:
        all_numbers = [int(char) for char in attribute[1:]]
        all_numbers = True
    except ValueError:
        all_numbers = False

    # String must have all three attributes to be a CUI
    return starts_with_C and length_of_eight and all_numbers
