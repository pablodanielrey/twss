import sys
import json
from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef, Literal

from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML

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

    gdata = Graph()

    #sql.setReturnFormat(RDFXML)
    for my_subject, external_subjects in subjects.items():
        for subject in external_subjects:
            print(f'obteniendo datos de {subject}')
            sql.setQuery("""
                select distinct ?s ?p ?o
                where {
                    <""" + subject + """> ?p ?o .
                }        
            """)
            results = sql.query().convert()
            for result in results["results"]["bindings"]:
                add_format_triplets(gdata, my_subject, result)

            ''' agrego el sameAs de mi subject al recurso externo de dbpedia '''
            gdata.add((my_subject, OWL.sameAs, URIRef(subject)))

    #gdata.serialize(sys.stdout.buffer, format='turtle')
    with open('data/dbpedia.ttl','w') as f:
       f.write(gdata.serialize(format='turtle').decode("utf-8"))