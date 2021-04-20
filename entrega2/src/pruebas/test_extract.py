import extruct
import json
import pprint
import sys

if __name__ == '__main__':

    archivo = sys.argv[1]
    with open(archivo, 'r') as f:
        text = f.read()
    #text = json.dumps(p)
    h = f"<html><head><script type='application/ld+json'>{text}</script></head><body></body></html>"
    data = extruct.extract(h)

    print(json.dumps(data))

    #pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(data)    