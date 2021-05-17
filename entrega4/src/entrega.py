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
        'twssd': Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/data/'),
        'dbr': Namespace('http://dbpedia.org/resource/'),
        'dbo': Namespace('http://dbpedia.org/ontology/'),
        'wiki': Namespace('http://en.wikipedia.org/wiki/'),
        'foaf': Namespace('http://xmlns.com/foaf/0.1/')
    }
    return schemas

def bind_schemas(g:Graph):
    for s, n in get_schemas().items():
        g.bind(s,n)


def dereference_resource(iri):
    headers = {'Accept':'text/turtle'}
    r = requests.get(f"{iri}", headers=headers)
    if not r.ok:
        #print(f'No se pudo obtener info de dbpedia de {iri}')
        #print(r.text)
        raise Exception()
    return r.text
    
def to_graph(data):
    gaux = Graph()
    gaux.parse(data=data, format='turtle')
    return gaux

def get_triples_to_add(gaux):
    dbo = Namespace('http://dbpedia.org/ontology/')
    foaf = Namespace('http://xmlns.com/foaf/0.1/')
    triples = []

    ''' data properties '''
    properties = [dbo.birthDate, foaf.isPrimaryTopicOf]
    for p in properties:
        for t in gaux.triples((None, p, None)):
            triples.append(t)

    ''' object properties '''
    properties = [dbo.occupation]
    for p in properties:
        for st, sp, so in gaux.triples((None, p, None)):
            oiri = str(so)
            triples2 = derreference_occupation(oiri)
            triples.extend(triples2)

    return triples

def change_subjects(subject, triples):
    ''' aplico las tripletas al subject correcto '''
    rtriples = []
    for st,sp,so in triples:
        rtriples.append((subject, sp, so))
    return rtriples

def derreference_occupation(occupation):
    turtle = dereference_resource(occupation)
    dbo = Namespace('http://dbpedia.org/ontology/')
    gaux = Graph()
    gaux.parse(data=turtle, format='turtle')
    for titles in gaux.triples((None, dbo.title, None)):
        return (titles,)


if __name__ == '__main__':
    g = Graph()
    bind_schemas(g)
    schemas = get_schemas()
    schema = schemas['schema']

    files_to_merge = [
        'data/dataset-original.ttl',
        'data/links.ttl'
    ]

    for dfile in files_to_merge:
        #print(f'Procesando : {dfile}')
        with open(dfile,'r') as f:
            g.parse(f, format='turtle')

    for st,sp,so in g.triples((None, OWL.sameAs, None)):
        if 'Antonio_Banderas' not in str(st):
            continue
        if 'dbpedia' in str(so):
            #print(f'Accediendo a {so}')
            iri = str(so)
            data = dereference_resource(iri)
            gaux = to_graph(data)
            triples = get_triples_to_add(gaux)
            for stt,spp,soo in change_subjects(st, triples):
                g.add((stt,spp,soo))
            break

    ''' la salida del script debe ser stdout así que imprimo todas las tripletas del grafo '''
    g.serialize(sys.stdout.buffer, format='turtle')
