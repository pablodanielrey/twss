import logging
import sys
import urllib
import time
import json
from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef, Literal

from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML


def get_endpoints():
    endpoints = {
        "dbpedia": SPARQLWrapper("http://dbpedia.org/sparql"),
        "wikidata": SPARQLWrapper("https://query.wikidata.org/sparql")
    }
    for e in endpoints:
        endpoints[e].setReturnFormat(JSON)
    return endpoints

def select_endpoint(iri:str, endpoints:dict):
    for e in endpoints:
        if e in iri:
            return endpoints[e]
    raise Exception(f'enpoint desconocido para la iri {iri}')

def get_schemas():
    schemas = {
        'schema': Namespace('http://schema.org/'),
        'twss': Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_final.ttl#'),
        'twssd': Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/data/'),
        'dbr': Namespace('http://dbpedia.org/resource/'),
        'dbo': Namespace('http://dbpedia.org/ontology/'),
        'wiki': Namespace('http://en.wikipedia.org/wiki/'),
        'foaf': Namespace('http://xmlns.com/foaf/0.1/'),
        'owl': Namespace('http://www.w3.org/2002/07/owl#')
    }
    return schemas

def bind_schemas(g:Graph):
    for s, n in get_schemas().items():
        g.bind(s,n)


def add_format_triplets(g:Graph, subject:URIRef, triplets:dict):
    """ agrega la tripleta dándole formato al grafo """
    ''' las propiedades deberían ser todas uris '''
    assert triplets['p']['type'] == 'uri'
    prop = URIRef(triplets['p']['value'])

    obj = triplets['o']
    if obj['type'] == 'uri':
        vobj = URIRef(obj['value'])
    else:
        vobj = Literal(obj['value'])
    
    g.add((URIRef(subject), prop, vobj))


if __name__ == '__main__':

    print('leyendo archivo de subjects')
    gsubjects = Graph()
    with open('data/wikidata_subjects.ttl','r') as f:
        gsubjects.parse(f, format='turtle')

    print('convirtiendo a formato interno')
    subjects = {}
    ''' convierto al formato que espera el script '''
    for s,p,o in gsubjects.triples((None,OWL.sameAs,None)):
        my_subject = str(s)
        external = str(o)
        print(f'{my_subject} <-- {external}')
        if my_subject not in subjects:
            subjects[my_subject] = set()
        subjects[my_subject].add(external)

    delay = 2
    gdata = Graph()
    bind_schemas(gdata)

    endpoints = get_endpoints()
    cantidad = len(subjects)
    procesado = 0
    for my_subject, external_subjects in subjects.items():
        for subject in external_subjects:
            print(f'procesando {procesado}/{cantidad}')
            sql = select_endpoint(subject, endpoints)
            sql.setQuery("""
                select distinct ?s ?p ?o
                where {
                    <""" + subject + """> ?p ?o .
                }        
            """)

            for tries in range(1,10):
                print(f'esperando {delay}')
                try:
                    time.sleep(delay)
                except Exception as e1:
                    pass

                try:
                    print(f'obteniendo datos de {subject}')
                    results = sql.query().convert()
                    for result in results["results"]["bindings"]:
                        add_format_triplets(gdata, my_subject, result)

                    delay = delay - 1 if delay > 2 else delay
                    break

                except urllib.error.HTTPError as he: 
                    logging.warning(f'Incremento el delay para no matar el endpoint {delay}')
                    delay = (delay * delay) + 1

            procesado += 1

    #gdata.serialize(sys.stdout.buffer, format='turtle')
    with open('data/external_dataset.ttl','w') as f:
       f.write(gdata.serialize(format='turtle').decode("utf-8"))
