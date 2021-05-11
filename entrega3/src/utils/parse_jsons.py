import sys
import json

import networkx as nx
import matplotlib.pyplot as plt

from rdflib import Graph, RDF, RDFS
from rdflib.term import URIRef
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from rdflib.plugin import register, Parser



register('json-ld', Parser, 'rdflib_jsonld.parser', 'JsonLDParser')  


def visualize(g:Graph):
    G = rdflib_to_networkx_multidigraph(g)
    pos = nx.spring_layout(G, scale=2)
    edge_labels = nx.get_edge_attributes(G, 'r')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw(G, with_labels=True)
    plt.show()


if __name__ == '__main__':
    jf = sys.argv[1]
    with open(jf, 'r') as jsonf:
        data1 = jsonf.read()

    g = Graph()
    g.bind('schema','http://schema.org/')
    g.parse(data=data1, format='json-ld')
    
    dfile = jf.replace('.json','.ttl')

    with open(dfile, 'w') as f:
        f.write(g.serialize(format="turtle").decode("utf-8"))

    ''' listar todas las películas '''
    movie = URIRef('http://schema.org/Movie')
    for mid, _t, _m in g.triples((None,None,movie)):
        for __m, t, o in g.triples((mid, None, None)):
            print(t,o)

    ''' listar solo los nombres de las películas '''

    name = URIRef('http://schema.org/name')
    for mid, _t, _m in g.triples((None,None,movie)):
        for _m, __t, n in g.triples((mid, name, None)):
            print(n)