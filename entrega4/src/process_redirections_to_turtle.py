import sys
import json
import requests
import re


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
    r = requests.get(url, headers={'Accept':'text/turtle'}, allow_redirects=False)
    alternates = r.headers.get('Alternates',None)
    if not alternates:
        print(f'No existe representación text/turtle para la url {url}')
        sys.exit(1)
    url = process_alternates(alternates)
    print(url)

