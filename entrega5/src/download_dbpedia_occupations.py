
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
            names.append(str(name))
    return names


if __name__ == '__main__':

    g = Graph()

    with open('data/dataset-original.ttl','r') as f:
        g.parse(f, format='turtle')

    sch = get_schemas()
    schema = sch['schema']

    names = get_persons_names(g, schema)
    occupations = set()

    sql = get_dbpedia_endpoint()

    for name in names:
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
            occupation = result["oc"]['value']
            if len(occupation) > 0:
                occupations.add(occupation)
    
    print(occupations)
    doccupations = {
        'occupations': list(occupations)
    }
    with open('data/db_pedia_occupations_original.json','w') as f:
        f.write(json.dumps(doccupations, ensure_ascii=False))