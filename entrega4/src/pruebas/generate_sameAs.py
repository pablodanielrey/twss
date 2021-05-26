import sys
import uuid
import json
import rdflib
import requests
import extruct
from w3lib.html import get_base_url
from urllib.parse import quote

from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef


def get_schemas():
    schemas = {
        'schema': Namespace('http://schema.org/'),
        'twss': Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_schema.ttl#'),
        'twsse': Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_schema_extended.ttl#'),
        'twssd': Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/data/')
    }
    return schemas

def bind_schemas(g:Graph):
    for s, n in get_schemas().items():
        g.bind(s,n)

def get_name(g, schema, piri):
    for st, sp, so in g.triples((piri, schema.name, None)):
        return str(so)

def name_to_dbpedia_resource(name):
    dbname = f'https://dbpedia.org/resource/{quote(name)}'
    return dbname


if __name__ == '__main__':

    g = Graph()
    bind_schemas(g)
    schemas = get_schemas()
    schema = schemas['schema']

    files_to_merge = [
        'data/dataset-original.ttl'
    ]

    for dfile in files_to_merge:
        print(f'Procesando : {dfile}')
        with open(dfile,'r') as f:
            g.parse(f, format='turtle')

    glinks = Graph()
    bind_schemas(glinks)
    for st, sp, so in g.triples((None, RDF.type, schema.Person)):
        name = get_name(g, schema, st)
        dbname = name_to_dbpedia_resource(name)
        glinks.add(((st, OWL.sameAs, URIRef(dbname))))
            
    with open('data/links.ttl','w') as f:
        f.write(glinks.serialize(format='turtle').decode("utf-8"))
