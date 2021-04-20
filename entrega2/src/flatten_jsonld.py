
import os
import sys
import json
from pyld import jsonld
from pyld_document_loader import my_requests_document_loader

if __name__ == '__main__':

    fjson = sys.argv[1]
    with open(fjson, 'r') as f:
        doc = json.loads(f.read())

    jsonld.set_document_loader(my_requests_document_loader())
    data = jsonld.flatten(doc)

    jpath, jfile = os.path.split(fjson)

    flatten_file = f'{jpath}{os.path.sep}flatten_{jfile}'
    with open(flatten_file,'w') as f:
        f.write(json.dumps(data))