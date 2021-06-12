import logging
import sys
from typing import Iterable
import urllib
import time
import json
from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef, Literal

from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML


from common import bind_schemas, get_schemas, get_persons_names


def get_wikidata_endpoint():
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)
    return sparql


"""
    PUnto 1
"""

def get_wikidat_persons_with_award(sql):
    """
        obtiene todas las personas que sean humanos que hayan recibido awards
    """
    sql.setQuery("""
        SELECT DISTINCT ?person WHERE {
            ?person wdt:P31 wd:Q5 .
            ?person wdt:P166/wdt:P31? wd:Q19020 .
        }    
    """)
    results = sql.query().convert()
    return [r['person']['value'] for r in results["results"]["bindings"]]


def get_directors(g:Graph):
    """
        obtiene todos los directores de mi base.
    """
    ss = get_schemas()
    s = ss['schema']
    ds = [d for m,p,d in g.triples((None, s.director, None))]
    return ds


def get_external_references(g:Graph, ds:Iterable):
    """
        solo arma un mapa para poder mapear mas simple recursos externos a entidades internas mías.
    """
    owl = get_schemas()['owl']
    refs = {}
    for d in ds:
        for s,p,o in g.triples((d, owl.sameAs, None)):
            refs[str(o)] = d
    return refs


"""
    Punto 2
"""


def get_actors_and_directors_with_awards_from_wikidata(sql):
    sql.setQuery("""
     select distinct ?film ?director ?actor where {
       ?film wdt:P161 ?actor .
       ?film wdt:P31 wd:Q11424 .
       ?film wdt:P57 ?director .
       ?director wdt:P166/wdt:P31? wd:Q19020 .
      
     }    
    """)
    results = sql.query().convert()

    films = {}

    for r in results["results"]["bindings"]:
        film = r['film']['value']
        if film not in films:
            films[film] = {'directors':set(), 'actors':set()}
        films[film]['directors'].add(r['director']['value'])
        films[film]['actors'].add(r['actor']['value'])

    return films

def get_internal_person_from_external_iri(g:Graph, persons:set):
    owl = get_schemas()['owl']
    internals = set()
    for person in persons:
        for s,p,o in g.triples((None, owl.sameAs, URIRef(person))):
            print(f'{s} <--- {person}')
            internals.add(s)
    return internals



if __name__ == '__main__':

    g = Graph()
    with open('data/dataset-final.ttl','r') as f:
        g.parse(f, format='turtle')

    with open('data/wikidata_subjects.ttl','r') as f:
        g.parse(f, format='turtle')        


    ss = get_schemas()
    schema = ss['schema']
    twss = ss['twss']

    sql = get_wikidata_endpoint()

    """
        punto 1 - ver notes_random.txt 
    """
    print("/////////////////////////////////////////\nPunto1\n//////////////////////////////////////////")

    print(f'buscando datos específicos de wikidata sobre premios')
    persons_with_award = get_wikidat_persons_with_award(sql)
    directors_with_awards = set()

    directors = get_directors(g)
    refs = get_external_references(g, directors)

    print(f'encontradas {len(persons_with_award)} personas con premios, dentro de {len(directors)} directores de mi dataset, busco en {len(refs)} referencias para relacionarlos')

    for person in persons_with_award:
        if person in refs:
            director = refs[person]
            print(f'{director} <--- {person}')
            print(f'El director {director} recibió premio según wikidata')
            directors_with_awards.add(director)

    ''' agrego las tripletas entre actores y directores en mi dataset '''
    for director in directors_with_awards:
        for film,p,o in g.triples((None, schema.director, director)):
            for ss,pp,actor in g.triples((film, schema.actor, None)):
                print(f'{actor} <-- wasDirectedByOscarWinner <-- {director}')
                g.add((actor, twss.wasDirectedByOscarWinner, director))
            for ss,pp,actor in g.triples((film, schema.actors, None)):
                print(f'{actor} <-- wasDirectedByOscarWinner <-- {director}')
                g.add((actor, twss.wasDirectedByOscarWinner, director))


    """
        ahora resuelvo el punto 2. 
        encontrar la info de directores/actores sobre films que no se encuentran en mi base.
    """

    print("\n\n\n/////////////////////////////////////////\nPunto2\n//////////////////////////////////////////")

    print(f'buscando datos generales en wikidata de todas las películas que existan en wikidata')
    films = get_actors_and_directors_with_awards_from_wikidata(sql)
    for title in films:
        film = films[title]
        directors = get_internal_person_from_external_iri(g, film['directors'])
        if len(directors) > 0:
            print(f'\n\n\n{title}')
            print(f'directores de {title} encontrados internos : {len(directors)}')
            print(directors)
        for director in directors:
            actors = get_internal_person_from_external_iri(g, film['actors'])
            print(f'actores internos encontrados {len(actors)}')
            for actor in actors:
                print(f'{actor} <--- wasDirectedByOscarWinner <--- {director}')
                g.add((actor, twss.wasDirectedByOscarWinner, director))
