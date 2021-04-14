
import uuid
import requests
import json
import bs4
import logging


"""
    ///////////////// procesamiento de html /////////////////////
"""

def get_page_and_parse(link):
    r = requests.get(link)
    if not r.ok:
        raise Exception(f'no se pudo obtener el contenido del link {link}')
    return bs4.BeautifulSoup(r.text, 'html.parser')

def find_all_jsons(b):
    rjsons = []
    jsons = b.find_all('script', attrs={'type':'application/ld+json'})
    for j in jsons:
        for c in j.contents:
            js = c.replace('\n','').strip()
            jdata = json.loads(js)
            rjsons.append(jdata)
    return rjsons


"""
    ////////////////// procesamiento de jsons //////////////////
"""

def join(jsons):
    rjson = {}
    for j in jsons:
        for k,v in j.items():
            if k not in rjson:
                rjson[k] = v
            else:
                if rjson[k] == v:
                    continue
                """ 
                    ///////////////////////////////////////////////////////////////////////
                    claves repetidas con distintos valores las convierto en una lista 
                    ///////////////////////////////////////////////////////////////////////
                    TODO: ver cual es la mejor opción para mantener la compatibilidad con schema.org
                """
                values = [rjson[k]]
                rjson[k] = values
                values.append(v)
    return rjson


def parse_and_flatten_person(p):
    if p['@type'] != 'Person':
        raise Exception('p.type != Person')

    if 'sameAs' in p:
        url = p['sameAs']
        person_datas = find_all_jsons(get_page_and_parse(url))
        person_datas.append(p)
        return join(person_datas)
    
    return p


def parse_person(p):
    return parse_and_flatten_person(p)


def parse_movie_actors(m):
    ps = []
    for p in m['actors']:
        ps.append(parse_person(p))
    m['actors'] = ps

def parse_movie_director(m):
    ps = []
    for p in m['director']:
        ps.append(parse_person(p))
    m['director'] = ps

def parse_movie_author(m):
    ps = []
    for p in m['author']:
        ps.append(parse_person(p))
    m['author'] = ps

def parse_reviews_author(m):
    if 'review' not in m:
        return
    for r in m['review']:
        if 'author' not in r:
            continue
        r['author'] = parse_person(r['author'])        

if __name__ == '__main__':

    url = 'https://www.rottentomatoes.com/m/wonder_woman_1984'
    b = get_page_and_parse(url)
    movies = find_all_jsons(b)
    for m in movies:
        parse_movie_actors(m)
        parse_movie_director(m)
        print(json.dumps(m))
