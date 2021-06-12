import logging
import sys
import urllib
import time
import json
from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef, Literal

from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML


from common import bind_schemas, get_schemas, get_persons_names


def get_dbpedia_endpoint():
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)
    return sparql


def get_directors(g:Graph):
    ss = get_schemas()
    s = ss['schema']
    ds = [d for m,p,d in g.triples((None, s.director, None))]
    return ds

def get_internal_subject(g:Graph, s:URIRef, owl:Namespace):
    for ss,p,o in g.triples((None, owl.sameAs, s)):
        return ss

def get_external_subjects(g:Graph, ds:list):
    owl = get_schemas()['owl']
    ss = set()
    for d in ds:
        print(f'analizando recurso externo de {d}')
        ess = set([es for s,p,es in g.triples((d, owl.sameAs, None)) if 'http://dbpedia.org/resource/' in str(es)])
        print(f'encontrados: {ess}')
        ss = ss.union(ess)
    return ss

if __name__ == '__main__':

    g = Graph()
    with open('data/dataset-final.ttl','r') as f:
        g.parse(f, format='turtle')

    with open('data/wikidata_subjects.ttl','r') as f:
        g.parse(f, format='turtle')        


    print(get_directors(g))
    sys.exit(1)

    direc = []

    sql = get_dbpedia_endpoint()
    sql.setQuery("""SELECT DISTINCT ?person WHERE {
        ?person wdt:P166/wdt:P31? wd:Q19020 .
    }""")
    r = sql.query().convert()
    for result in r["results"]["bindings"]:
        direc.append(result['person']['value'])

    owl = get_schemas()['owl']
    idir = [get_internal_subject(g,d,owl) for d in direc]

    print(idir)