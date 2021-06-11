import logging
import sys
import urllib
import time
import json
from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef, Literal

from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML


from common import bind_schemas, get_schemas, get_persons_names


def get_dbpedia_endpoint():
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    return sparql


def get_directors(g:Graph):
    ss = get_schemas()
    s = ss['schema']
    ds = [d for m,p,d in g.triples((None, s.director, None))]
    return ds


def get_external_subjects(g:Graph, ds:list):
    owl = get_schemas()['owl']
    ss = set()
    for d in ds:
        ess = set([es for s,p,es in g.triples((None, owl.sameAs, None))])
        ss = ss.union(ess)
    return ss

if __name__ == '__main__':

    g = Graph()
    with open('data/dataset-final.ttl','r') as f:
        g.parse(f, format='turtle')

    ds = get_directors(g)
    es = get_external_subjects(g,ds)
    print(es)