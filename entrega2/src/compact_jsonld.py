
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
    data = jsonld.compact(doc, "https://schema.org")

    jpath, jfile = os.path.split(fjson)

    flatten_file = f'{jpath}{os.path.sep}compact_{jfile}'
    with open(flatten_file,'w') as f:
        f.write(json.dumps(data))