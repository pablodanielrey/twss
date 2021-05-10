import sys
import json
from urllib.parse import quote

from rdflib import Graph, RDF, RDFS, Namespace, Literal
from rdflib.term import URIRef


def load_data():
    with open('data/merged_tp1.json') as f:
        data = json.loads(f.read())
    return data


def get_ontology():
    o = Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_simple.ttl#')
    d = Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/data/')
    return (o,d)

if __name__ == '__main__':

    o,d = get_ontology()
    g = Graph()
    g.bind("twss", o)
    g.bind("twssd", d)

    data = load_data()
    for movie in data['MOVIES']:
        title = movie['TITLE']

        print(title.replace(' ','_'))
        vtitle = quote(title.replace(' ','_'))
        dmovie = d[vtitle]
        g.add((dmovie, RDF.type, o.Movie))
        g.add((dmovie, o.title, Literal(title)))

    print(g.serialize(format="turtle").decode("utf-8"))