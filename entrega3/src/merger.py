import sys
import uuid
import json
import rdflib
from urllib.parse import quote
from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef


def bind_schemas(g:Graph):
    g.bind('schema',Namespace('http://schema.org/'))
    g.bind("t", Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss.ttl#'))
    g.bind("twss", Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_simple.ttl#'))
    g.bind("twsss", Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_schema.ttl#'))
    g.bind("twssd", Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/data/'))



if __name__ == '__main__':

    gfinal = Graph()
    bind_schemas(gfinal)

    ''' busco las ontologías definidas en protegé y las mergeo en un grafo '''
    ontologies = [
        '../owl/twss_simple.ttl',
        '../owl/twss_schema.ttl',
        '../owl/twss.ttl'
    ]
    for o in ontologies:
        gontology = Graph()
        bind_schemas(gontology)
        with open(o, 'r') as f:
            gontology.parse(f, format='turtle')
        gfinal = gfinal + gontology

    ''' busco los grafos con los datos de los tps '''
    datas = [
        'data/merged_tp1.ttl',
        'data/merged_tp2.ttl'
    ]
    for o in datas:
        g = Graph()
        bind_schemas(g)
        with open(o, 'r') as f:
            g.parse(f, format='turtle')
        gfinal = gfinal + g

    ''' escribo los datos finales '''
    with open('data/merged_final.ttl','w') as f:
        f.write(gfinal.serialize(format="turtle").decode("utf-8"))    
