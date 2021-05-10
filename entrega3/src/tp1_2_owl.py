import sys
import json

from rdflib import Graph, RDF, RDFS, Namespace
from rdflib.term import URIRef


def load_data():
    with open('data/merged_tp1.json') as f:
        data = json.loads(f.read())
    return data



if __name__ == '__main__':

    n = Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_simple.ttl')
    print(n)
    
