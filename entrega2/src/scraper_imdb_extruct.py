import extruct
import requests
from w3lib.html import get_base_url
import pprint
import json
from urllib.parse import urlparse


def merge_dicts(dst, src):
    ''' copia la claves de src hacia dst. si se duplican las claves entonces los valores quedan en una lista '''
    dst.update(src)
    for k,v in src.items():
        if k in dst and k in src:
            if type(dst[k]) == list:
                if type(src[k]) == list:
                    dst[k] = list(set(dst[k]).union(set(src[k])))
                    #dst[k].extend(src[k])
                else:
                    dst[k].append(v)

def get_jsons(url):
    r = requests.get(url)
    base_url = get_base_url(r.text, r.url)
    data = extruct.extract(r.text, base_url=base_url)
    return data['json-ld']

def dereference_urls(m:dict, base_url=''):
    if 'url' in m:
        url = f"{base_url}{m['url']}"
        print(f'\n\n\naccediendo a {url}')
        data = get_jsons(url)
        print(f'datos obtenidos \n{data}\n\n\n')
        for p in data:
            merge_dicts(m, p)
           

"""
movie
    actor
        Person
    director
        Person
    creator
        Person | Organization
    review
"""



if __name__ == '__main__':

    url = 'https://www.imdb.com/title/tt7126948/'
    (scheme, netloc, path, params, query, fragment) = urlparse(url)
    base = f"{scheme}://{netloc}"
    movies = get_jsons(url)
    for m in movies:
        #dereference_urls(m, base)
        for a in m['actor']:
            if type(a) == dict:
                dereference_urls(a, base)
        for a in m['director']:
            if type(a) == dict:
                dereference_urls(a, base)
        for a in m['creator']:
            if type(a) == dict:
                dereference_urls(a, base)
    print(json.dumps(movies[0]))

