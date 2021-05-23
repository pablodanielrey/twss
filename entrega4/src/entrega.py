import sys
import uuid
import json
import rdflib
import requests
import extruct
from w3lib.html import get_base_url
from urllib.parse import quote

from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef, Literal

def get_schemas():
    schemas = {
        'schema': Namespace('http://schema.org/'),
        'twss': Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_schema.ttl#'),
        'twsse': Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_schema_extended.ttl#'),
        'twsse2': Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_schema_extended2.ttl#'),
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


def dereference_resource(iri):
    headers = {'Accept':'text/turtle'}
    r = requests.get(f"{iri}", headers=headers)
    if not r.ok:
        #print(f'No se pudo obtener info de dbpedia de {iri}')
        #print(r.text)
        raise Exception()
    return r.text
    
def to_graph(data):
    gaux = Graph()
    gaux.parse(data=data, format='turtle')
    return gaux

def get_triples_to_add(gaux):
    dbo = get_schemas()['dbo']
    foaf = get_schemas()['foaf']
    triples = []

    ''' data properties '''
    properties = [dbo.birthDate, foaf.isPrimaryTopicOf]
    for p in properties:
        for t in gaux.triples((None, p, None)):
            triples.append(t)

    ''' object properties '''
    properties = [dbo.occupation]
    for p in properties:
        for st, sp, so in gaux.triples((None, p, None)):
            oiri = str(so)
            #print(oiri)
            triples2 = derreference_occupation(oiri)
            triples.extend(triples2)

    return triples


def occupation_to_my_ontology(schema, triple):
    ''' 
        defino una opcupación como un blank node y se la asigno a la persona.
        genero una ocupación por cada nombre definido.
    '''
    (st, sp, so) = triple
    triples = []
    for o_name in str(so).split(','):
        o = BNode(f'occupation_{str(uuid.uuid4())}')
        triples.extend([
            (o, RDF.type, schema.Occupation),
            (o, schema.name, Literal(o_name.strip())), 
            (st, schema.hasOccupation, o)
        ])
    return triples

def birth_to_my_ontology(schema, triple):
    ''' solo cambio a usar la propiedad de mi ontología '''
    (st, sp, so) = triple
    return [(st, schema.birthDate, so)]

def change_to_my_ontology(subject, triples):
    ''' 
        aplico las tripletas al subject correcto y reemplazo las propieades por las correctas a mi ontología 
    '''
    dbo = get_schemas()['dbo']
    schema = get_schemas()['schema']
    properties_map = {
        dbo.title: occupation_to_my_ontology,
        dbo.birthDate: birth_to_my_ontology
    }
    rtriples = []
    for st,sp,so in triples:
        ''' cambio el subject y cambio la propiedad '''
        if sp in properties_map:
            func = properties_map[sp]
            to_add = func(schema, (subject,sp,so))
        else:
            to_add = [(subject, sp, so)]
        rtriples.extend(to_add)
    return rtriples

def derreference_occupation(occupation):
    ''' accede a la iri que representa la ocupación y obtiene las tripletas que son el título '''
    turtle = dereference_resource(occupation)
    dbo = get_schemas()['dbo']
    gaux = Graph()
    gaux.parse(data=turtle, format='turtle')

    triples = []

    ''' me aseguro de que lo referenciado sea dbo:PersonFunction '''
    for st, sp, so in gaux.triples((None, RDF.type, dbo.PersonFunction)):
        for titles in gaux.triples((st, dbo.title, None)):
            triples.append(titles)

    return triples


'''
    ////////////////////////////////////// estas funciones son para agregar la compatibildiad con las demas ontologias //////////////////////////////
'''


def __get_type(g:Graph, subject):
    return [so for (st, sp, so) in g.triples((subject, RDF.type, None))]

def agregar_mi_ontologia(g:Graph):
    ''' agrega mi ontología al grago importando desde la ontologia primaria. '''
    my_ontology = URIRef('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_final.ttl')

    for st, sp, so in g.triples((None, RDF.type, OWL.Ontology)):
        g.add((st, OWL.imports, my_ontology))
        return


def verify_pregunta2(g:Graph, st, sp):
    ''' 
        verifica si la propiedad a asociar tiene dentor del grafo el dominio correcto, en caso contrario se lo agrega 
        tambien busca todas las ontologías definidas dentor del grafo y les importa la mía (donde están definidas las propieades agregar por el script)
    '''
    agregar_mi_ontologia(g)
    _types = __get_type(g, st)
    for stt,spp,soo in g.triples((sp, RDFS.domain, None)):
        if soo in _types:
            _types.remove(soo)

    for _t in _types:
        ''' agrego los tipos que no estaban en el dominio de la propiead '''
        g.add((sp, RDFS.domain, _t))


'''
//////////////////////////////////////////////////////////////////////////////////////////////////////
'''


if __name__ == '__main__':

    ''' tomo los archivos por linea de comandos '''
    files_to_merge = [
        sys.argv[1],
        sys.argv[2]
    ]

    g = Graph()
    bind_schemas(g)
    schemas = get_schemas()
    schema = schemas['schema']

    """
    files_to_merge = [
        'data/dataset-original.ttl',
        'data/links.ttl'
    ]
    """

    for dfile in files_to_merge:
        #print(f'Procesando : {dfile}')
        with open(dfile,'r') as f:
            g.parse(f, format='turtle')

    '''
        tomo las iris de los recursos de dbpedia
        las desreferencio y obtengo las tripletas que me interesan de dbpedia
        cambio esas tripletas para que se ajusten a mi ontología y se asocien con la iri de mi individual.
    '''
    for st,sp,so in g.triples((None, OWL.sameAs, None)):
        if 'dbpedia' in str(so):
            iri = str(so)
            data = dereference_resource(iri)
            gaux = to_graph(data)
            triples = get_triples_to_add(gaux)
            for stt,spp,soo in change_to_my_ontology(st, triples):
                verify_pregunta2(g, stt, spp)
                g.add((stt,spp,soo))

    ''' la salida del script debe ser stdout así que imprimo todas las tripletas del grafo '''
    g.serialize(sys.stdout.buffer, format='turtle')
