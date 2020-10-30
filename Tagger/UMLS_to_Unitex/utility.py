import os
import re

def get_category(types):
    drug_labels = [
        'Clinical Drug',
        'Pharmacologic Substance',
        'Antibiotic',
        'Vitamin',
        'Hazardous or Poisonous Substance'
    ]

    disorder_labels = [
        'Congenital Abnormality',
        'Virus',
        'Neoplastic Process',
        'Anatomical Abnormality',
        'Acquired Abnormality',
        'Sign or Symptom',
        'Finding'
    ]

    device_labels = [
        'Medical Device',
        'Drug Delivery Device',
        'Research Device'
    ]

    procedure_labels = [
        'Therapeutic or Preventive Procedure',
        'Laboratory Procedure',
        'Diagnostic Procedure',
        'Health Care Activity'
    ]

    all_labels = {
        'Drug': drug_labels,
        'Disorder': disorder_labels,
        'Device': device_labels,
        'Procedure': procedure_labels
    }

    curr_category = None
    for category, labels in all_labels.items():
        shared_labels = overlap(labels, types)
        if len(shared_labels):
            curr_category = category
            break

    return curr_category

def overlap(list1, list2):
    overlapping = []
    for item in list1:
        if item in list2:
            overlapping.append(item)
    return overlapping

def unescaped_split(delimiter, line):
    # Only split on unescaped versions of delimiter in line
    return re.split(r'(?<!\\){}'.format(delimiter), line)

def unescaped_sub(to_replace, replacement, line):
    return re.sub(r'(?<!\\){}'.format(to_replace), replacement, line)

def make_output_files(output_folder):
    output_files = {
        'Drug': 'drug.dic',
        'Disorder': 'disorder.dic',
        'Device': 'device.dic',
        'Procedure': 'procedure.dic'
    }

    for category, file_path in output_files.items():
        joined_path = os.path.join(output_folder, file_path)
        output_files[category] = open(joined_path, 'w')
    return output_files
