import sys
import json
import requests
import re

def get_content(req):

    if (req.status_code >= 300 and req.status_code < 400):
        ''' es una redirección '''
        url = req.headers['Location']
        assert url != None
        req = requests.get(url, headers={'Accept':'text/turtle'}, allow_redirects=False)
        return get_content(req)

    if req.status_code == 200:
        return req.text

    return None
    """
        esto por lo que veo no es necesario 
    if content and req.status_code != 200:
        ''' analizo el contenido alternativo '''
        alternates = r.headers.get('Alternates',None)
        if not alternates:
            print(f'No existe representación text/turtle para la url {url}')
            return None
        url = process_alternates(alternates)


    r = requests.get(url, headers={'Accept':'text/turtle'}, allow_redirects=False)
    return url
    """


def process_alternates(alternates):
    reg = re.compile('{\"(.*)\".*?{type (.*?)}}')
    alts = alternates.split(',')
    for a in alts:
        m = reg.match(a.strip())
        if m:
            url = m.group(1)
            content = m.group(2)
            if 'turtle' in content:
                return url
    return None

if __name__ == '__main__':

    url = sys.argv[1]
    r = requests.get(url, headers={'Accept':'text/turtle'}, allow_redirects=True)
    print(get_content(r))
