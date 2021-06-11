import logging
from rdflib import Graph

from common import bind_schemas


if __name__ == '__main__':

    g = Graph()
    bind_schemas(g)

    print('leyendo archivo 1')
    with open('data/external_dataset_final.ttl', 'r') as f:
        g.parse(f, format='turtle')

    print('leyendo archivo 2')
    with open('data/dataset-original.ttl', 'r') as f:
        g.parse(f, format='turtle')


    print('escribiendo dataset unificado final')
    with open('data/dataset-final.ttl','w') as f:
        f.write(g.serialize(format='turtle').decode("utf-8"))
