
import os
import sys
import json
import uuid


def gen_uid():
    return f'urn:uuid:{str(uuid.uuid4())}'

def gen_reference(id):
    return {'@id':id}


def process_person(p, data):
    assert p['@type'] == 'Person'

    clazz = 'Person'
    name = p['name']
    for d in data[clazz]:
        if name == d['name']:
            return gen_reference(d['@id'])        

    data[clazz].append(p)
    p['@id'] = gen_uid()
    return gen_reference(p['@id'])


process_matrix = {
    'Person': process_person
}


def process_entity(source:dict, k:str, data:dict):
    """ ejecuta el procesador de la entidad y reemplaza por la referencia a la misma """
    if '@type' not in source[k]:
        return
    clazz = source[k]['@type']
    if clazz not in process_matrix:
        return

    clazz = p['@type']
    if clazz not in data:
        data[clazz] = []

    process = process_matrix[clazz]
    ref = process(source[k], data)
    source[k] = ref

def process_list(source:dict, k:str, data:dict):
    """ procesa toda una lista de clases y reemplaza por la lsita de referencias a las mismas """
    if len(source[k]) <= 0:
        return
    
    if not source[k][0]:
        """ solo de seguridad. no vi que existan valores nulos como primeros elementos """
        return

    if type(source[k][0]) is not dict:
        return

    if '@type' not in source[k][0]:
        return

    clazz = source[k][0]['@type']
    if clazz not in process_matrix:
        return

    if clazz not in data:
        data[clazz] = []

    refs = []
    for d in source[k]:
        process = process_matrix[clazz]
        ref = process(d, data)
        refs.append(ref)

    source[k] = refs

MOVIE = 'MOVIE'

if __name__ == '__main__':

    data = {
        MOVIE: None
    }

    #fjson = sys.argv[1]
    fjson = 'entrega2/data/rotten.json'
    with open(fjson, 'r') as f:
        doc = json.loads(f.read())

    for k in doc:
        if '@' in k:
            continue
        if type(doc[k]) is dict:
            process_entity(doc, k, data)
        if type(doc[k]) is list:
            process_list(doc, k, data)

    data[MOVIE] = doc

    jpath, jfile = os.path.split(fjson)
    normalized_file = f'{jpath}{os.path.sep}normalized_{jfile}'
    with open(normalized_file,'w') as f:
        f.write(json.dumps(data))