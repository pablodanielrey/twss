
import json

if __name__ == '__main__':
    with open('data/imdb.json', 'r') as f:
        data = json.loads(f.read())
    print(data)