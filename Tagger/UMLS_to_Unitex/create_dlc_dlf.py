import os
from utility import unescaped_split

def is_complex(line):
    term, _ = unescaped_split(',', line)
    complex_indicators = ' ,-_.|;@:'

    for indicator in complex_indicators:
        found = term.find(indicator)
        if found >= 0:
            return True
    return False


def create_dlc_dlf(folder_path):
    print('Creating dlc and dlf files...')

    input_file_names = [
        'device.dic',
        'drug.dic',
        'disorder.dic',
        'procedure.dic'
    ]

    input_file_paths = [os.path.join(folder_path, file) for file in input_file_names]

    dlc_file = open(os.path.join(folder_path, 'dlc'), 'w')
    dlf_file = open(os.path.join(folder_path, 'dlf'), 'w')

    dlc_content = ''
    dlf_content = ''

    for file in input_file_paths:
        input_dic = open(file, 'r')

        for line in input_dic:
            if is_complex(line):
                dlc_content += line
            else:
                dlf_content += line

        input_dic.close()

    dlc_file.write(dlc_content)
    dlf_file.write(dlf_content)

    dlc_file.close()
    dlf_file.close()
