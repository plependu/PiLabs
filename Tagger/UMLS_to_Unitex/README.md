The scripts in this directory, 'UMLS_to_Unitex', are for the conversion of UMLS information into Unitex format dictionaries.
See the README in 'tagger-api/Resources/Dictionaries' for the use-case of these scripts.

### To use:
1. Edit `main.py`<br>
  On lines 11 and 12, change the `conso_path` and `types_path` to point to your local MRCONSO.RRF and MRSTY.RRF files, respectively.
2. Run `python ./main.py`<br>
  This will take a few minutes, since the files are relatively large.<br>
  Additionally, it might be helpful to close other programs, since this program can have high amounts of memory usage.

### Results:
Inside the 'UMLS_to_Unitex/Categorized_Dictionaries' directory, there will now be 14 files.
1. 'device.bin'
2. 'device.dic'
3. 'device.inf'
4. 'disorder.bin'
5. 'disorder.dic'
6. 'disorder.inf'
7. 'dlc'
8. 'dlf'
9. 'drug.bin'
10. 'drug.dic'
11. 'drug.inf'
12. 'procedure.bin'
13. 'procedure.dic'
14. 'procedure.inf'

### Explanation
The '.dic' files are the raw Unitex-format dictionaries, divided by category.<br>
The '.bin' and '.inf' files are the result of compressing the '.dic' files, using the Unitex `Compress` program.<br>
'dlc' contains compound words, in Unitex-format.<br>
'dlf' contains simple words, in Unitex-format.
