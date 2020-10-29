# Tagger API
This API provides a service to extract medical information from electronic health records (EHRs).<br>

File listing:
+ `tagger-api`: Contains the API source code
+ `UMLS_to_Unitex`: Scripts to transform UMLS data into Unitex format dictionaries

## API
### Requirements
+ python 3
+ [python-unitex](https://github.com/patwat/python-unitex)
+ [Flask](https://flask.palletsprojects.com/en/1.1.x/installation/#install-flask) (`pip install flask`)
+ [flask-restful](https://flask-restful.readthedocs.io/en/latest/installation.html) (`pip install flask-restful`)

### To start the API
1. Follow the steps in `tagger-api/Resources/Dictionaries/README.md` to setup the dictionaries this API uses.
2. `cd` into the `tagger-api` directory
3. execute `python3 ./start_api.py`

### Usage
The API provides two main endpoints: `/ehrs` and `/terms`
___
#### To make requests of the API

  #### Lookup
  + `lookup` functionality is accessible through a `GET` request to the following URL<br>
    URL : http://localhost:8020/ehrp-api/v1/terms<br>
    ##### Parameters
    + Required:<br>
      + Name: 'term'
        + Type: string
        + Description: This should be the term you want to lookup.<br>

    ##### Example request:
    + GET: http://localhost:8020/ehrp-api/v1/terms?term=hypertension
    + RESPONSE:<br>
    ```
    [
        {
          'instances': [
            {'onto': 'Meddra', 'term': 'hypertension', 'umid': '10020772'}
          ],
          'name': 'lookup'
        }
    ]
    ```
___

#### Extract
  + `extract` functionality is accessible through a `POST` request to the following URL<br>
    URL : http://localhost:8020/ehrp-api/v1/ehrs
    ##### Parameters
    + Optional:
      + Name: 'text'
        + Type: string or list of strings
        + Description: This should be the text(s) you want to process. Multiple texts can be specified, all using 'text' as a parameter name.
        + **NOTE**: Exactly one of 'text' and 'file' can be used in the same request. If both are used, or neither are used, a 422 error response will be returned.
      + Name: 'types'
        + Type: string, or list of strings
        + Description: This parameter specifies which type(s) of medical data you want to be extracted from the text. Multiple types can be specified, all using 'types' as a parameter name.
        + Example using the python requests library:<br>
        ```
        args = {
          'text': [medical_text_string1, medical_text_string2],
          'types': 'drug'
        }
        response = requests.post('http://localhost:8021/ehrp-api/v1/ehrs', data=args)
        ```
        + Possible values for 'types':  
          + 'drug': Looks for drug names
          + 'disorder': Looks for disorder names
        + If 'types' is not specified, all types will be used.
        + If multiple types are desired, it is faster to not specify any, and just extract the desired information from the returned results
      + Name: 'file'
        + Type: file object
        + Description: Allows a text file to be uploaded in place of the 'text' parameter.
        + **NOTE**: The file is expected to have one EHR per line.
        + **NOTE**: Exactly one of 'text' and 'file' can be used in the same request. If both are used, or neither are used, a 422 error response will be returned.
        + Example using the python requests library:
        ```
        args = {
          'types': ['drug', 'pt_summary', 'ami']
        }

        text_file = open('medical_text_path', 'rb')
        response = requests.post('http://localhost:8021/ehrp-api/v1/ehrs', data=args, files={'file': text_file))
        ```

Both GET and POST requests return JSON objects.

### Error response codes
* 400: Malformed url; check your base url and parameter names to see if they conform to the descriptions above.
* 422: Two possible reasons:
  1. 'types' parameter has unknown value; check the value(s) you are using for 'types', make sure it is one of the allowable types listed above.
  2. In a POST request to the `extract` functionality, either both 'text' and 'file' have been specified, or neither have been specified.




___
## Example Interface
1. install nodejs
2. `cd` into the ehrp-ui-master directory
3. execute `npm install`
4. execute `npm start` to start the local server
5. Visit URL at http://localhost:3020/<br>
Port numbers and REST api can be configured in bin/settings.js file
