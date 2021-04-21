
import os
import sys
import json
import uuid


def gen_uid():
    return f'urn:uuid:{str(uuid.uuid4())}'

def gen_reference(id):
    return {'@id':id}

"""
    /////////////////////// FORMATEADORES /////////////////////////////////
"""


def process_person(p, data):
    assert p['@type'] == 'Person'

    clazz = p['@type']
    name = p['name']
    for d in data[clazz]:
        if name == d['name']:
            return gen_reference(d['@id'])        

    data[clazz].append(p)
    p['@id'] = gen_uid()
    return gen_reference(p['@id'])

def process_review(p, data):
    assert p['@type'] == 'Review'

    clazz = p['@type']
    r = p['reviewBody']
    for d in data[clazz]:
        if r == d['reviewBody']:
            return gen_reference(d['@id'])        

    process_entity(p, data)

    data[clazz].append(p)
    p['@id'] = gen_uid()
    return gen_reference(p['@id'])



process_matrix = {
    'Person': process_person,
    'Review': process_review
}


"""
    //////////////////////////////////////////////////////////////
"""

def process_entity_value(source:dict, k:str, data:dict):
    """ ejecuta el procesador de la entidad y reemplaza por la referencia a la misma """
    if '@type' not in source[k]:
        return

    clazz = source[k]['@type']
    if clazz not in process_matrix:
        return

    if clazz not in data:
        data[clazz] = []

    process = process_matrix[clazz]
    ref = process(source[k], data)
    source[k] = ref

def process_list(source:dict, k:str, data:dict):
    """ procesa toda una lista de clases y reemplaza por la lsita de referencias a las mismas """
    if len(source[k]) <= 0:
        return

    refs = []
    for d in source[k]:
        if not d:
            continue

        if type(d) is not dict:
            """ para tener en cuenta las listas combinadas de elementos de distintos tipos """
            refs.append(d)
            continue

        if '@type' not in d:
            """ para tener en cuenta las listas combinadas de elementos de distintos tipos """
            refs.append(d)
            continue

        clazz = d['@type']
        if clazz not in process_matrix:
            refs.append(d)
            continue

        if clazz not in data:
            data[clazz] = []
        process = process_matrix[clazz]
        ref = process(d, data)
        refs.append(ref)

    source[k] = refs




def process_entity(d:dict, data:dict):
    for k in d:
        if '@' in k:
            continue
        if type(d[k]) is dict:
            process_entity_value(d, k, data)
        if type(d[k]) is list:
            process_list(d, k, data)


if __name__ == '__main__':


    files = [
        'data/scraped_rotten.json',
        'data/scraped_metacritic.json',
        'data/scraped_imdb.json',
        'data/scraped_ecartelera.json'
    ]

    #fjson = sys.argv[1]
    for fjson in files:
        data = {
        }

        #fjson = 'entrega2/data/rotten.json'
        with open(fjson, 'r') as f:
            doc = json.loads(f.read())

        process_entity(doc, data)
        data['Movie'] = doc

        jpath, jfile = os.path.split(fjson)
        normalized_file = f'{jpath}{os.path.sep}normalized_{jfile}'
        with open(normalized_file,'w') as f:
            f.write(json.dumps(data, ensure_ascii=False))