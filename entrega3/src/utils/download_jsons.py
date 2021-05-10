import json
import rdflib
import requests
import extruct
from w3lib.html import get_base_url

def get_urls_of_data() -> list:
    urls = [
        'https://www.ecartelera.com/peliculas/wonder-woman-1984',
        'https://www.rottentomatoes.com/m/wonder_woman_1984',
        'https://www.metacritic.com/movie/wonder-woman-1984',
        'https://www.imdb.com/title/tt7126948/'
    ]
    return urls

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

if __name__ == '__main__':
    for url in get_urls_of_data():
        j = get_jsons(url)
        fi = url.replace('/','_').replace(':','_')
        with open(f'data/{fi}.json','w') as f:
            f.write(json.dumps(j,ensure_ascii=False))
