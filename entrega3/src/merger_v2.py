import sys
import uuid
import json
import rdflib
from urllib.parse import quote
from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef

def bind_schemas(g:Graph):
    g.bind('schema',Namespace('http://schema.org/'))
    g.bind("twsse", Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_schema_extended.ttl#'))
    g.bind("twss", Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_schema.ttl#'))
    g.bind("twssd", Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/data/'))



if __name__ == '__main__':

    gfinal = Graph()
    bind_schemas(gfinal)

    ''' 
        busco las ontologías definidas en protegé y las mergeo en un grafo 
        como lo indique en las notas me parece que debería ser incluída en formato web y no en archivo para esta solución.
        asi que solo leo la extendida.
    '''
    ontologies = [
        '../owl/twss_schema_extended.ttl'
    ]
    for o in ontologies:
        gontology = Graph()
        bind_schemas(gontology)
        with open(o, 'r') as f:
            gontology.parse(f, format='turtle')
        gfinal = gfinal + gontology

    ''' busco los grafos con los datos de los tps '''
    datas = [
        'data/merged_tp1_extended.ttl',
        'data/merged_tp2.ttl'
    ]
    for o in datas:
        g = Graph()
        bind_schemas(g)
        with open(o, 'r') as f:
            g.parse(f, format='turtle')
        gfinal = gfinal + g

    ''' escribo los datos finales '''
    with open('data/merged_final_v2.ttl','w') as f:
        f.write(gfinal.serialize(format="turtle").decode("utf-8"))    
