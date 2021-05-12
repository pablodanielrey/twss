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

"""

def to_lean_graph(data_namespace, g:Graph):
    blank_nodes = set()

    ''' identifico todos los blank nodes que son clases de algun tipo '''
    for s,p,o in g.triples((None, RDF.type, None)):
        if isinstance(s, BNode):
            blank_nodes.add(s)

    schema = Namespace('http://schema.org/')
    for bn in blank_nodes:

        ''' genero una iri dentro del namespace de los individuals para el blank node '''
        for st, sp, so in g.triples((bn,schema.name,None)):
            bnid = quote(so.replace(' ','_'))
            break
        else:
            ''' no tiene nombre asi que genero un uuid '''
            for st, sp, so in g.triples((bn, RDF.type, None)):
                prefix = str(so).replace('http://schema.org/','')
                break
            else:
                prefix = None
            bnid = str(uuid.uuid4()) if not prefix else f"{prefix}_{str(uuid.uuid4())}"

        dbnid = data_namespace[bnid]

        ''' genero las tripletas con ese nuevo id y remuevo las tripletas anteriores '''
        for st,sp,so in g.triples((bn, None, None)):
            g.add((dbnid, sp, so))
            g.remove((st,sp,so))

        for st,sp,so in g.triples((None, None, bn)):
            g.add((st, sp, dbnid))
            g.remove((st,sp,so))

"""

"""
def mark_as_equal(g:Graph):
    '''
        analizo el grafo para ver si puedo identificar los recursos iguales.
        el criterio que uso es rdf:type y schema:name
    '''
    schema = Namespace('http://schema.org/')
    data = {}
    for iri, sp, _type in g.triples((None, RDF.type, None)):
        for stt, spp, _name in g.triples((iri, schema.name, None)):
            if _type not in data:
                data[_type] = {}
            if _name not in data[_type]:
                data[_type][_name] = []
            data[_type][_name].append(iri)

    for k in data:
        for n in data[k]:
            if len(data[k][n]) <= 1:
                continue
            for i, iri in enumerate(data[k][n]):
                if len(data[k][n]) > i+1:
                    iri2 = data[k][n][i+1]
                    g.add((iri, OWL.sameAs, iri2))
                    g.add((iri2, OWL.sameAs, iri))
"""


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

    with open('data/links.ttl','w') as f:
        for st, sp, so in g.triples((None, RDF.type, schema.Person)):
            print(st)
            f.write(f'{st}\n')
    
