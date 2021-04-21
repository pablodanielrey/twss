
import os
import sys
import json
import uuid


def merge_dicts(dst, src):
    ''' copia la claves de src hacia dst. si se duplican las claves entonces los valores quedan en una lista '''
    dst.update(src)
    for k,v in src.items():
        if k in dst and k in src:
            if type(dst[k]) == list:
                if type(src[k]) == list:
                    #dst[k] = list(set(dst[k]).union(set(src[k])))
                    dst[k].extend(src[k])
                else:
                    dst[k].append(v)


if __name__ == '__main__':


    files = [
        'data/normalized_scraped_imdb.json',
        'data/normalized_scraped_rotten.json',
        'data/normalized_scraped_metacritic.json',
        'data/normalized_scraped_ecartelera.json'
    ]

    data = {
    }

    for fjson in files:
        with open(fjson, 'r') as f:
            doc = json.loads(f.read())

        merge_dicts(data, doc)

    jpath, jfile = os.path.split(fjson)
    normalized_file = f'{jpath}{os.path.sep}final.json'
    with open(normalized_file,'w') as f:
        f.write(json.dumps(data, ensure_ascii=False))