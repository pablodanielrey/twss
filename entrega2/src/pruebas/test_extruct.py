
import requests
import extruct
import pprint
from w3lib.html import get_base_url
import sys

if __name__ == '__main__':

    url = sys.argv[1]
    r = requests.get(url)
    base_url = get_base_url(r.text, r.url)
    data = extruct.extract(r.text, base_url=base_url)

    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(data)


    