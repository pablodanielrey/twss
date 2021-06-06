import sys
import json
from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef, Literal

from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML

from common import get_persons_names, get_schemas, bind_schemas

def get_dbpedia_endpoint():
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    return sparql

if __name__ == '__main__':

    g = Graph()
    with open('data/dataset-original.ttl','r') as f:
        g.parse(f, format='turtle')

    sch = get_schemas()
    schema = sch['schema']
    names = get_persons_names(g, schema)

    ''' cargo las ocupaciones procesadas a mano '''
    with open('data/db_pedia_occupations.json','r') as f:
        occupations = json.load(f)['occupations']
        
    subjects = {}
    sql = get_dbpedia_endpoint()

    for my_subject, name in names:
        local_subjects = set()

        print(f'obteniendo {name}')
        sql.setQuery("""
            PREFIX dbp: <http://dbpedia.org/property/>
            select distinct ?s ?oc
            where {
                ?s dbp:name \"""" + name + """\"@en .
                ?s dbp:occupation ?oc .
            }        
        """)
        results = sql.query().convert()
        for result in results["results"]["bindings"]:
            occ = result['oc']['value']
            if occ in occupations:
                ''' se encuentra en alguna de las ocupaciones permitidas '''
                subject = result['s']['value']
                local_subjects.add(subject)
        
        print(f'entidades externas encontradas {local_subjects}')
        subjects[my_subject] = local_subjects

    ''' escribo los subjects '''        
    gsubjects = Graph()
    bind_schemas(gsubjects)

    for my_subject, external_subjects in subjects.items():
        for subject in external_subjects:
            ''' agrego el sameAs de mi subject al recurso externo '''
            gsubjects.add((my_subject, OWL.sameAs, URIRef(subject)))

    with open('data/dbpedia_subjects.ttl','w') as f:
       f.write(gsubjects.serialize(format='turtle').decode("utf-8"))
