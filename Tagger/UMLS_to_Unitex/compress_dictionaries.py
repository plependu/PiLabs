from unitex.tools import compress
import os

def compress_dictionaries(folder_path):
    file_names = [
        'drug.dic',
        'disorder.dic',
        'device.dic',
        'procedure.dic'
    ]

    file_paths = [os.path.join(folder_path, file) for file in file_names]

    for file in file_paths:
        print('Compresing {}...'.format(file))
        compress(file)
