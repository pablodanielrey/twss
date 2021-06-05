from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef, Literal

def get_persons_names(g:Graph, schema:Namespace):
    names = []
    for s,p,o in g.triples((None, RDF.type, schema['Person'])):
        for ss,pp,name in g.triples((s, schema['name'], None)):
            names.append((s,str(name)))
    return names

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

