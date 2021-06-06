import logging
import sys
import urllib
import time
import json
from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef, Literal

from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML

from .common import bind_schemas, get_schemas, get_persons_names


def get_wikidata_endpoint():
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)
    return sparql

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
    
    g.add((subject, prop, vobj))

def get_remote_subjects(name:str, delay:int):
    local_subjects = set()
    for tries in range(1,10):
        try:
            #Q33999 = actor
            #P279 = subclase
            #P106 = ocupación

            """
                imdb
                        ?s p:P345 ?sen1 .
                        ?sen1 ps:P345 ?imdb .
            """

            print(f'obteniendo {name}')
            sql.setQuery("""
                select distinct ?s
                    where {
                        { ?s rdfs:label \"""" + name + """\"@en . }
                        UNION
                        { ?s rdfs:label \"""" + name + """\"@es . }
                        ?s p:P106 ?sen1 .                                   # ocupacion
                        {
                            select distinct ?sen1 
                            where {
                                { 
                                    ?sen1 ps:P106 wd:Q33999 .       # actor
                                }
                                UNION 
                                {
                                    ?sen1 ps:P106 ?occ .            # ocupaciones subclase de actor.
                                    ?occ p:P279 ?sen2 .
                                    ?sen2 ps:P279 wd:Q33999 .
                                }
                                UNION 
                                {
                                    ?sen1 ps:P106 ?occ .            # ocupaciones subclase de director.
                                    ?occ p:P279 ?sen2 .
                                    ?sen2 ps:P279 wd:Q3455803
                                }
                                UNION 
                                {
                                    ?sen1 ps:P106 ?occ .             # ocupaciones instancia de filmmaking occupation (Q4220920)
                                    ?occ p:P31 ?sen2 .
                                    ?sen2 ps:P31 wd:Q4220920 .
                                }
                            }
                        }
                    }
            """)

            try:
                print(f'esperando {delay}')
                time.sleep(delay)
            except Exception as e1:
                pass

            results = sql.query().convert()
            for result in results["results"]["bindings"]:
                subject = result['s']['value']
                local_subjects.add(subject)
            
            print(f'entidades externas encontradas {local_subjects}')
            
            ''' para id disminuyendo el backoff '''
            delay = delay - 1 if delay > 2 else delay

            return (delay, local_subjects)
            
        except urllib.error.HTTPError as he: 
            logging.warning(f'Incremento el delay para no matar el endpoint {delay} {tries}')
            delay = delay * delay

    return (delay, local_subjects)


if __name__ == '__main__':

    g = Graph()

    with open('data/dataset-original.ttl','r') as f:
        g.parse(f, format='turtle')

    sch = get_schemas()
    schema = sch['schema']
    names = get_persons_names(g, schema)

    delay = 2
    subjects = {}

    sql = get_wikidata_endpoint()

    """
        busco primero las iris remotas asi consulto por sobre esa entidad para obtener las tripletas.
    """

    actual = 0
    cantidad = len(names)
    for my_subject, name in names:
        print(f'procesando {actual}/{cantidad}')
        actual += 1
        delay, remote_subjects = get_remote_subjects(name, delay)
        subjects[my_subject] = remote_subjects

    ''' escribo los subjects debido a que wikidata pone límites a los requests '''        
    gsubjects = Graph()
    for my_subject, external_subjects in subjects.items():
        for subject in external_subjects:
            ''' agrego el sameAs de mi subject al recurso externo '''
            gsubjects.add((my_subject, OWL.sameAs, URIRef(subject)))

    with open('data/wikidata_subjects.ttl','w') as f:
       f.write(gsubjects.serialize(format='turtle').decode("utf-8"))



   