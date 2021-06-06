import logging
import sys
import urllib
import time
import json
from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef, Literal

from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML

from common import get_schemas, bind_schemas, add_format_triplets

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


if __name__ == '__main__':


    print('leyendo archivo de subjects')
    gsubjects = Graph()
    with open('data/dbpedia_subjects.ttl','r') as f:
        gsubjects.parse(f, format='turtle')

    delay = 2
    gdata = Graph()
    bind_schemas(gdata)

    endpoints = get_endpoints()
    cantidad = 'x'
    procesado = 0

    for s,p,o in gsubjects.triples((None,OWL.sameAs,None)):
        my_subject = str(s)
        subject = str(o)

        print(f'procesando {procesado}/{cantidad}')
        sql = select_endpoint(subject, endpoints)
        sql.setQuery("""
            select distinct ?s ?p ?o
            where {
                <""" + subject + """> ?p ?o .
            }        
        """)

        ''' pruebo 10 intentos por cada request fallido '''
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
    with open('data/external_dataset2.ttl','w') as f:
       f.write(gdata.serialize(format='turtle').decode("utf-8"))
