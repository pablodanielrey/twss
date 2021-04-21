
import os
import sys
import json
import uuid

from common import get_urls_of_data, get_file_name

def merge_dicts(dst, src):
    ''' copia la claves de src hacia dst. si se duplican las claves entonces los valores quedan en una lista '''
    for k,v in src.items():
        if k not in dst:
            dst[k] = v
        if k in dst:
            if type(dst[k]) is list:
                if type(src[k]) is list:
                    #dst[k] = list(set(dst[k]).union(set(src[k])))
                    dst[k].extend(src[k])
                else:
                    dst[k].append(v)
                continue

            if type(dst[k]) is dict:
                if type(src[k]) is dict:
                    merge_dicts(dst[k], src[k])
                    continue

                if type(src[k]) is list:
                    src[k].append(dst[k])
                    dst[k] = src[k]
                    continue

            if type(dst[k]) == type(src[k]):
                dst[k] = [dst[k], src[k]]
                continue

            raise Exception(f'no se como mergear {k} {type(dst[k])} y {type(src[k])}')


        
def imdb_source(dst:dict, src:dict, k:str):
    if 'www.imdb.com' in src['isBasedOnUrl']:
        dst[k] = src[k]

def property_list(dst:dict, src:dict, k:str):
    if k not in dst:
        dst[k] = src[k]
        return

    acc = []
    for d in [dst,src]:
        if type(d[k]) is list:
            for de in d[k]:
                if type(de) == dict:
                    de['origen'] = d['origen']
                acc.append(de)
        else:
            if type(d[k]) == dict:
                d[k]['origen'] = d['origen']
            acc.append(d[k])
    dst[k] = acc

def agregate_rating_merger(dst:dict, src:dict, k:str):
    assert dst[k]['@type'] == 'AggregateRating'
    assert src[k]['@type'] == 'AggregateRating'

    d = {
        '@type': 'AggregateRating',
        'bestRating': 0,
        'worstRating': 0,
        'ratingCount': 0,
        'ratingValue': 0
    }

    d['bestRating'] = max(dst[k]['bestRating'], src[k]['bestRating'])
    d['worstRating'] = min(dst[k]['worstRating'], src[k]['worstRating'])
    d['ratingCount'] = dst[k]['ratingCount'] + src[k]['ratingCount']
    d['ratingValue'] = (dst[k]['ratingValue'] + src[k]['ratingValue']) / 2
    dst[k] = d
    

def merge_schema_entities(dst:dict, src:dict, k:str):
    if not dst[k]:
        dst[k] = []
    if type(dst[k]) is not list:
        dst[k] = [dst[k]]
    if type(src[k]) is list:
        dst[k].extend(src[k])
        return
    dst[k].append(src[k])

movie_fields_matrix = {
    'genre': imdb_source,
    'name': imdb_source,
    'contentRating': imdb_source,
    'description': imdb_source,
    'datePublished': imdb_source,
    'duration': imdb_source,
    'url': property_list,
    'image': property_list,
    'trailer': property_list,
    'isBasedOnUrl': property_list,
    'aggregateRating': agregate_rating_merger,
    'productionCompany': property_list,
    'director': merge_schema_entities,
    'actor': merge_schema_entities,
    'review': merge_schema_entities

}


def merge_movies(dst:dict, src:dict):
    for k,v in src.items():
        if k not in dst:
            dst[k] = v
            continue

        if k not in movie_fields_matrix:
            print(f'{k} no existe ninguna forma de hacer merge')
            continue

        merger = movie_fields_matrix[k]
        merger(dst, src, k)

"""
merge_matrix = {
    'Movie': merge_movies
}

def merge(dst:dict, src:dict):
    for k,v in dst.items():
        if k not in merge_matrix:
            continue
        assert k in src
        merger = merge_matrix[k]
        v.extend(src[k])
        acc = {}
        for m in v:
            merger(acc,m)
"""

if __name__ == '__main__':

    files = [
        f"data/normalized_{get_file_name(url)}.json" for url in get_urls_of_data()
    ]

    data = {
        'Movie': {}
    }

    for fjson in files:
        with open(fjson, 'r') as f:
            doc = json.loads(f.read())

        merge_movies(data['Movie'], doc['Movie'])

    """
        escribo el archivo final unificado
    """
    jpath, jfile = os.path.split(fjson)
    normalized_file = f'{jpath}{os.path.sep}final.json'
    with open(normalized_file,'w') as f:
        f.write(json.dumps(data, ensure_ascii=False))