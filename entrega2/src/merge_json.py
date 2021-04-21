


if __name__ == '__main__':


    files = [
        'data/normalized_scraped_imdb.json',
        'data/normalized_scraped_rotten.json',
        'data/normalized_scraped_metacritic.json',
        'data/normalized_scraped_ecartelera.json'
    ]

    #fjson = sys.argv[1]
    for fjson in files:
        data = {
        }

        with open(fjson, 'r') as f:
            doc = json.loads(f.read())

        process_entity(doc, data)
        data['movie'] = doc

        jpath, jfile = os.path.split(fjson)
        normalized_file = f'{jpath}{os.path.sep}normalized_{jfile}'
        with open(normalized_file,'w') as f:
            f.write(json.dumps(data, ensure_ascii=False))