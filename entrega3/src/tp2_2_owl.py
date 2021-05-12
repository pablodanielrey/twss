import sys
import uuid
import json
import rdflib
import requests
import extruct
from w3lib.html import get_base_url
from urllib.parse import quote

from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef
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
    g.bind("twsss", Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_schema.ttl#'))
    g.bind("twssd", Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/data/'))


def to_lean_graph(data_namespace, g:Graph):
    blank_nodes = set()

    ''' identifico todos los blank nodes que son clases de algun tipo '''
    for s,p,o in g.triples((None, RDF.type, None)):
        if isinstance(s, BNode):
            blank_nodes.add(s)

    schema = Namespace('http://schema.org/')
    for bn in blank_nodes:

        ''' genero una iri dentro del namespace de los individuals para el blank node '''
        for st, sp, so in g.triples((bn,schema.name,None)):
            bnid = quote(so.replace(' ','_'))
            break
        else:
            ''' no tiene nombre asi que genero un uuid '''
            for st, sp, so in g.triples((bn, RDF.type, None)):
                prefix = str(so)
                break
            else:
                prefix = None
            bnid = str(uuid.uuid4()) if not prefix else f"{prefix}_{str(uuid.uuid4())}"

        dbnid = data_namespace[bnid]

        ''' genero las tripletas con ese nuevo id y remuevo las tripletas anteriores '''
        for st,sp,so in g.triples((bn, None, None)):
            g.add((dbnid, sp, so))
            g.remove((st,sp,so))

        for st,sp,so in g.triples((None, None, bn)):
            g.add((st, sp, dbnid))
            g.remove((st,sp,so))

def add_named_individuals(g:Graph):
    #schema = Namespace('http://schema.org/')
    #used_types = [schema.Movie, schema.Person, schema.Clip, schema.PublicationEvent, ]
    #for type in used_types:
    for s,p,o in g.triples((None, RDF.type, None)):
        g.add((s,RDF.type, OWL.NamedIndividual))    

def mark_as_equal(g:Graph):
    '''
        analizo el grafo para ver si puedo identificar los recursos iguales.
        el criterio que uso es rdf:type y schema:name
    '''
    schema = Namespace('http://schema.org/')
    data = {}
    for iri, sp, _type in g.triples((None, RDF.type, None)):
        for stt, spp, _name in g.triples((iri, schema.name, None)):
            if _type not in data:
                data[_type] = {}
            if _name not in data[_type]:
                data[_type][_name] = []
            data[_type][_name].append(iri)

    for k in data:
        for n in data[k]:
            if len(data[k][n]) <= 1:
                continue
            for i, iri in enumerate(data[k][n]):
                if len(data[k][n]) > i+1:
                    iri2 = data[k][n][i+1]
                    g.add((iri, OWL.sameAs, iri2))
                    g.add((iri2, OWL.sameAs, iri))


"""
/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

    VERIFICAR CON CASCO Y CON DIEGO SI ESTO ESTA OK !!!!
    CREO QUE ESTARIA MAL MODIFICAR LAS IRIs solo para que protegé me lo muestre con nombre!!

/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////
"""
def validate_iris_for_protege(g:Graph):
    ''' 
        hago una simple validación y cambio de iris 
        para que protege me los muestre ok.
        si termina en / le saco la /
        NOTA: NO se si esto esta ok, ya que las iris no son urls para buscar cosas, si 
        no son identificadores que no tienen mayor sentido que identificar!!
    '''
    subjects = set()
    objects = set()
    for st,sp,so in g:
        if isinstance(st,URIRef) and str(st).endswith('/'):
            subjects.add(st)

        if isinstance(so,URIRef) and str(so).endswith('/'):
            objects.add(so)
        
    for s in subjects:
        niri = URIRef(str(s[:-1]))
        for st, sp, so in g.triples((s,None,None)):
            assert st == s
            g.add((niri, sp, so))
            g.remove((st, sp, so))

    for o in objects:
        niri = URIRef(str(o[:-1]))
        for st, sp, so in g.triples((None,None,o)):
            assert so == o
            g.add((st, sp, niri))
            g.remove((st, sp, so))



if __name__ == '__main__':

    """
    para cargar la info directamente desde la url
    url = sys.argv[1]
    print(f'Descargando información de : {url}')
    json_ld = get_jsons(url)[0]
    """

    unionGraph = Graph()
    bind_schemas(unionGraph)

    urls_files_map = [
        ('https://www.ecartelera.com/peliculas/wonder-woman-1984', 'data/tp2/https___www.ecartelera.com_peliculas_wonder-woman-1984.json'),
        ('https://www.imdb.com/title/tt7126948/', 'data/tp2/https___www.imdb.com_title_tt7126948_.json'),
        ('https://www.metacritic.com/movie/wonder-woman-1984', 'data/tp2/https___www.metacritic.com_movie_wonder-woman-1984.json'),
        ('https://www.rottentomatoes.com/m/wonder_woman_1984', 'data/tp2/https___www.rottentomatoes.com_m_wonder_woman_1984.json')
    ]

    for url, dfile in urls_files_map:
        print(f'Descargando información de : {url}')
        with open(dfile,'r') as f:
            json_ld = json.loads(f.read())[0]

        ''' 
            implemento la solución que comentó Leonardo en el foro. 
            así no necesito parchear la librería rdflib
            problema de la redirección usando cabecera LINK
        '''
        json_ld['@context'] = json_ld['@context'].replace('http://schema.org','http://schema.org/docs/jsonldcontext.jsonld')
        json_ld['@context'] = json_ld['@context'].replace('https://schema.org','http://schema.org/docs/jsonldcontext.jsonld')
        djson_ld = json.dumps(json_ld, ensure_ascii=False)

        ''' ahora si puedo tratar de importar y parsear en el grafo de rdflib '''
        g = Graph()
        bind_schemas(g)
        g.parse(data=djson_ld, format='json-ld', publicID=url)
        
        validate_iris_for_protege(g)

        unionGraph = unionGraph + g

    data_namespace = Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/data/')
    to_lean_graph(data_namespace, unionGraph)
    add_named_individuals(unionGraph)

    #mark_as_equal(unionGraph)

    ''' busco la ontología definida en protegé y le hago merge con los datos de los individuals arriba procesados '''
    gontology = Graph()
    with open('../owl/twss_schema.ttl', 'r') as f:
        gontology.parse(f, format='turtle')

    gfinal = gontology + unionGraph
    with open('data/merged_tp2.ttl','w') as f:
        f.write(gfinal.serialize(format="turtle").decode("utf-8"))

    
