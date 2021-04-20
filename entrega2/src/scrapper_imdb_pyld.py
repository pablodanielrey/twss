
from pyld import jsonld
import extruct
import requests
from w3lib.html import get_base_url
import json


from pyld_document_loader import my_requests_document_loader


def get_schema_context():
    r = requests.get('https://schema.org/docs/jsonldcontext.json')
    return r.json()

def get_jsons(url):
    r = requests.get(url)
    base_url = get_base_url(r.text, r.url)
    data = extruct.extract(r.text, base_url=base_url)
    return data['json-ld']

if __name__ == '__main__':

    jsonld.set_document_loader(my_requests_document_loader())

    ctx = get_schema_context()

    url = 'https://www.imdb.com/title/tt7126948/'
    doc = get_jsons(url)
    #compacted = jsonld.compact(doc, ctx)
    data = jsonld.flatten(doc, ctx=ctx)
    print(json.dumps(data, indent=2))
    with open('imdb_pyld.json','w') as f:
        f.write(json.dumps(data))