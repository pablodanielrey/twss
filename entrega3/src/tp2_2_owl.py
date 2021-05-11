import sys
import json
import rdflib
import requests
import extruct
from w3lib.html import get_base_url

from rdflib import Graph, RDF, RDFS, OWL, Namespace
from rdflib.term import URIRef
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from rdflib.plugin import register, Parser

register('json-ld', Parser, 'rdflib_jsonld.parser', 'JsonLDParser')  


def get_jsons(url):
    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
    r = requests.get(url, headers=headers)
    if not r.ok:
        return []
    base_url = get_base_url(r.text, r.url)
    data = extruct.extract(r.text, base_url=base_url)
    if 'json-ld' not in data:
        raise Exception('No se encuentran datos json-ld')
    return data['json-ld']

def bind_schemas(g:Graph):
    g.bind('schema',Namespace('http://schema.org/'))
    g.bind("twss", Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_simple.ttl#'))
    g.bind("twssd", Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/data/'))

if __name__ == '__main__':

    """
    para cargar la info directamente desde la url
    url = sys.argv[1]
    print(f'Descargando información de : {url}')
    json_ld = get_jsons(url)[0]
    """

    url = 'https://www.ecartelera.com/peliculas/wonder-woman-1984'
    print(f'Descargando información de : {url}')
    with open('data/tp2/https___www.ecartelera.com_peliculas_wonder-woman-1984.json','r') as f:
        json_ld = json.loads(f.read())[0]

    ''' 
        implemento la solución que comentó Leonardo en el foro. 
        así no necesito parchear la librería rdflib
        problema de la redirección usando cabecera LINK
    '''
    json_ld['@context'] = json_ld['@context'].replace('http://schema.org','https://schema.org/docs/jsonldcontext.jsonld')
    djson_ld = json.dumps(json_ld, ensure_ascii=False)

    ''' ahora si puedo tratar de importar y parsear en el grafo de rdflib '''
    g = Graph()
    bind_schemas(g)
    g.parse(data=djson_ld, format='json-ld', publicID=url)

    """ agrego las entidades que maneja protegé a las entidades leidas en el json-ld """
    schema = Namespace('http://schema.org/')
    used_types = [schema.Movie, schema.Clip, schema.Person, schema.Country]
    for type in used_types:
        for s,p,o in g.triples((None, RDF.type, type)):
            g.add((s,RDF.type, OWL.NamedIndividual))

    #print(g.serialize(format="turtle").decode("utf-8"))
    
    g2 = Graph()
    bind_schemas(g2)
    with open('data/tp1/all.ttl','r') as f:
        g2.parse(f, format='turtle')
    #print(g2.serialize(format="turtle").decode("utf-8"))

    g3 = g + g2
    with open('data/merged.ttl','w') as f:
        f.write(g3.serialize(format="turtle").decode("utf-8"))
