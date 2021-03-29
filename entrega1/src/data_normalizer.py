import json

def normalize_data(d):
    if type(d) is str:
        return d.replace('\r','').replace('\n','').strip()
    if type(d) is dict:
        return normalize_dict(d)
    if type(d) is list:
        return normalize_list(d)
    raise Exception('se desconoce el tipo de datos a normalizar')

def normalize_list(l:list):
    return [normalize_data(d) for d in l]

def normalize_dict(o:dict):
    normalized = {}
    for k in o.keys():
        data = o[k]
        normalized[normalize_data(k)] = normalize_data(data)
    return normalized

with open('data/bruto_cinema_.json','r') as f:
    data = json.loads(f.read())
    normalized_data = normalize_dict(data)

with open('data/norm_cinema_.json','w') as f:
    f.write(json.dumps(normalized_data, ensure_ascii=False))
