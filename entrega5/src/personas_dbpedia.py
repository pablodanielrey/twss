
import json
from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef, Literal

from SPARQLWrapper import SPARQLWrapper, JSON

def get_dbpedia_endpoint():
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    return sparql

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

def get_persons_names(g:Graph, schema:Namespace):
    names = []
    for s,p,o in g.triples((None, RDF.type, schema['Person'])):
        for ss,pp,name in g.triples((s, schema['name'], None)):
            names.append((s,str(name)))
    return names


if __name__ == '__main__':

    g = Graph()

    with open('data/dataset-original.ttl','r') as f:
        g.parse(f, format='turtle')

    sch = get_schemas()
    schema = sch['schema']
    names = get_persons_names(g, schema)

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
                subject = result['s']['value']
                local_subjects.add(subject)
        
        print(f'entidades externas encontradas {local_subjects}')
        subjects[my_subject] = local_subjects

        break


    for my_subject, external_subjects in subjects.items():
        for subject in external_subjects:
            print(f'obteniendo datos de {subject}')
            sql.setQuery("""
                PREFIX dbp: <http://dbpedia.org/property/>
                select distinct ?s ?p ?o
                where {
                    <""" + subject + """> ?p ?o .
                }        
            """)
            results = sql.query().convert()
            for result in results["results"]["bindings"]:
                print(f'my subject : {my_subject} ')
                print(f'external subject : {subject}')
                print(result)
                break
