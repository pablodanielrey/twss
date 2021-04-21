import extruct
import requests
from w3lib.html import get_base_url
import pprint
import json
from urllib.parse import urlparse


from common import get_urls_of_data, get_file_name

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


def get_url(link:str, m:dict, base_url=''):
    url = convert_to_absolute(link, base_url)
    print(f'\n\n\naccediendo a {url}')
    data = get_jsons(url)
    print(f'datos obtenidos \n{data}\n\n\n')
    for p in data:
        merge_dicts(m, p)

def dereference_urls(m:dict, base_url=''):
    for url in ['url', 'sameAs']:
        if url in m:
            get_url(m[url], m, base_url)

def dereference_entity(ds, base:str):
    if type(ds) == list:
        for d in ds:
            if type(d) == dict:
                dereference_urls(d, base)
    elif type(ds) == dict:
        dereference_urls(ds, base)


"""
    ///////////////////
    ejemplo de función de normalización de datos
    ///////////////////
"""


def normalize_movie(m):
    if 'aggregateRating' in m:
        ar = m['aggregateRating']
        for k in ['bestRating', 'worstRating', 'ratingCount', 'ratingValue']:
            if type(ar[k]) is str:
                ar[k] = float(ar[k].replace(',','.').strip())
            else:
                ar[k] = float(ar[k])

            
if __name__ == '__main__':

    urls = get_urls_of_data()
    for url in urls:
        print(f"Obteniendo datos de {url}")

        (scheme, netloc, path, params, query, fragment) = urlparse(url)
        base = f"{scheme}://{netloc}"
        movies = get_jsons(url)
        
        for m in movies:
            m['isBasedOnUrl'] = url
            m['origen'] = url
            if 'actors' in m:
                m['actor'] = m['actors']
                del m['actors']
            for k in ['director', 'author', 'actor', 'creator']:
                if k in m:
                    dereference_entity(m[k], base)
            normalize_movie(m)

        scraped_file = f"scraped_{get_file_name(url)}.json"
        with open(f'data/{scraped_file}', 'w') as f:
            f.write(json.dumps(movies[0],ensure_ascii=False))

