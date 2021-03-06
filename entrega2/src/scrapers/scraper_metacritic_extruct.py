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
    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
    r = requests.get(url, headers=headers)
    if not r.ok:
        return []
    base_url = get_base_url(r.text, r.url)
    data = extruct.extract(r.text, base_url=base_url)
    if 'json-ld' not in data:
        raise Exception('No se encuentran datos json-ld')
    return data['json-ld']


def convert_to_absolute(url, base_url=''):
    scheme, netlock, path, params, query, frament = urlparse(url)
    if scheme == '':
        return f"{base_url}{url}"
    return url

def dereference_urls(m:dict, base_url=''):
    link = None
    if 'url' in m:
        link = m['url']
    if 'sameAs' in m:
        link = m['sameAs']
    if link:
        url = convert_to_absolute(link, base_url)
        print(f'\n\n\naccediendo a {url}')
        data = get_jsons(url)
        print(f'datos obtenidos \n{data}\n\n\n')
        for p in data:
            merge_dicts(m, p)
           

"""
movie
    actor
        Person
            url
    director
        Person
            url
    publisher
        Organization
            url
    productionCompany
        Organization
    trailer
        VideoObject
"""


def dereference_entity(ds, base:str):
    if type(ds) == list:
        for d in ds:
            if type(d) == dict:
                dereference_urls(d, base)
    elif type(ds) == dict:
        dereference_urls(ds, base)


if __name__ == '__main__':

    url = 'https://www.metacritic.com/movie/wonder-woman-1984'
    (scheme, netloc, path, params, query, fragment) = urlparse(url)
    base = f"{scheme}://{netloc}"
    movies = get_jsons(url)
    print(json.dumps(movies[0]))
    movies[0]['isBasedOnUrl'] = url
    """
    for m in movies:
        #dereference_urls(m, base)
        dereference_entity(m['actor'], base)
        dereference_entity(m['director'], base)
        dereference_entity(m['publisher'], base)
    print(json.dumps(movies[0]))
    """
    with open('data/scraped_metacritic.json', 'w') as f:
        f.write(json.dumps(movies[0],ensure_ascii=False))

