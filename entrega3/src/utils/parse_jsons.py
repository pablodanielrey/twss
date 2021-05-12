import sys
import json

from rdflib import Graph, RDF, RDFS
from rdflib.term import URIRef
from rdflib.plugin import register, Parser

register('json-ld', Parser, 'rdflib_jsonld.parser', 'JsonLDParser')  


if __name__ == '__main__':
    jf = sys.argv[1]
    with open(jf, 'r') as jsonf:
        json_ld = json.loads(jsonf.read())[0]

    g = Graph()
    g.bind('schema','http://schema.org/')

    ''' 
        implemento la solución que comentó Leonardo en el foro. 
        así no necesito parchear la librería rdflib
        problema de la redirección usando cabecera LINK
    '''
    json_ld['@context'] = json_ld['@context'].replace('http://schema.org','http://schema.org/docs/jsonldcontext.jsonld')
    json_ld['@context'] = json_ld['@context'].replace('https://schema.org','http://schema.org/docs/jsonldcontext.jsonld')
    djson_ld = json.dumps(json_ld, ensure_ascii=False)


    g.parse(data=djson_ld, format='json-ld')
    
    ttldfile = jf.replace('.json','.ttl')

    with open(ttldfile, 'w') as f:
        f.write(g.serialize(format="turtle").decode("utf-8"))

    jsondfile = jf.replace('.json','.json-ld')
    with open(jsondfile, 'w') as f:
        f.write(g.serialize(format="json-ld").decode("utf-8"))

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