import json
import datetime
from common import Merge, Movie, Show, Scrape, get_movie_id

if __name__ == '__main__':

    files = [
        'data/scraper_cinema.json', 
        'data/scraper_cinepolis.json'
    ]

    scrapes = []
    movies = []
    shows = []
    
    for fp in files:
        with open(fp, 'r') as f:
            scraped_data = json.loads(f.read())

            """ agrego las peliculas que falten """
            smovies = scraped_data[Scrape.MOVIES.value]
            for sm in smovies:
                mids = (get_movie_id(m) for m in movies)
                if get_movie_id(sm) not in mids:
                    movies.append(sm)

            """ agrego la info de los shows """
            shows.extend(scraped_data[Scrape.SHOWS.value])

            """ agrego la info de los scrapes """
            del scraped_data[Scrape.MOVIES.value]
            del scraped_data[Scrape.SHOWS.value]
            scrapes.append(scraped_data)

    merged = {
        Merge.DATE.value: str(datetime.datetime.utcnow()),
        Merge.MOVIES.value: movies,
        Merge.SHOWS.value: shows
    }
    with open('data/merged.json', 'w') as f:
        f.write(json.dumps(merged, ensure_ascii=False))