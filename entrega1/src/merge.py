import json
import datetime
import unicodedata
from common import Merge, Movie, Show, Scrape, get_movie_id

def normalize(s):
    return s.lower().replace('.','').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')

def ten(s1, s2):
    n1 = normalize(s1)
    n2 = normalize(s2)
    return n1 == n2

def test_equal(m1, m2):
    """ 
        testea por igualdad 2 películas
        para considerarlas iguales deben tener el mismo director, al menos un actor en común y los títulos idénticos sin tener en cuenta los caracteres especiales.
    """

    """ testeo los directores """
    d1 = m1[Movie.DIRECTOR.value]
    d2 = m2[Movie.DIRECTOR.value]
    if not ten(d1,d2):
        return False

    """ testeo que al menos tenga algun actor en comun """
    a1 = [normalize(a) for a in m1[Movie.ACTORS.value]]
    a2 = [normalize(a) for a in m2[Movie.ACTORS.value]]
    if len(set(a1).intersection(set(a2))) == 0:
        return False

    """ los titulos son iguales? """
    t1 = normalize(m1[Movie.TITLE.value])
    t2 = normalize(m2[Movie.TITLE.value])
    if t1 == t2:
        return True

    return False

    
def merge_movies(ml):
    """
        hace merge de una lista de películas que ya se determinó que eran equivalentes.
        retorna un elmento que representa la película con todos los datos mergeados
        proceso primero los datos que siempre existen
    """

    """ titulo cualquiera """
    title = ml[0][Movie.TITLE.value]

    """ uno todos los actores """
    nactors = []
    actors = []
    for m in ml:
        for a in m[Movie.ACTORS.value]:
            nactor = normalize(a)
            if nactor not in nactors:
                nactors.append(nactor)
                actors.append(a)
    
    """ uno los géneros """
    genres = set()
    for m in ml:
        genres.update(m[Movie.GENRE.value])
    genres = list(genres)

    """ duración elijo la mayor """
    duration = -1
    for m in ml:
        md = int(m[Movie.DURATION.value])
        if  md > duration:
            duration = md

    mr = {
        Movie.TITLE.value: title,
        Movie.ACTORS.value: actors,
        Movie.DIRECTOR.value: ml[0][Movie.DIRECTOR.value],
        Movie.GENRE.value: genres,
        Movie.DURATION.value: duration
    }

    """
        ahora proceso los datos que veo que están opcionalmente en las pelis
    """

    """ elijo el primer lenguaje no vacío """
    for m in ml:
        if Movie.LANGUAGE.value in m:
            mr[Movie.LANGUAGE.value] = m[Movie.LANGUAGE.value]
            break

    """ original title """
    for m in ml:
        if Movie.ORIGINAL_TITLE.value in m:
            mr[Movie.ORIGINAL_TITLE.value] = m[Movie.ORIGINAL_TITLE.value]
            break

    """ elijo la primer distribuidora que aparezca """
    for m in ml:
        if Movie.DISTRIBUTION.value in m:
            mr[Movie.DISTRIBUTION.value] = m[Movie.DISTRIBUTION.value]
            break

    """ elijo el rating mas corto en string """
    rating = sorted((m[Movie.RATING.value] for m in ml if Movie.RATING.value in m), key=lambda r: len(r))[0]
    mr[Movie.RATING.value] = rating

    """ origen """
    origin = set()
    for m in ml:
        origin.update(m[Movie.ORIGIN.value])
    if len(origin) > 0:
        mr[Movie.ORIGIN.value] = list(origin)

    return mr


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
            if len(movies) <= 0:
                movies.extend(sorted(scraped_data[Scrape.MOVIES.value], key=lambda m: m[Movie.DIRECTOR.value]))
            else:
                smovies = sorted(scraped_data[Scrape.MOVIES.value], key=lambda m: m[Movie.DIRECTOR.value])
                for sm in smovies:
                    candidates = [m for m in movies if test_equal(sm, m)]
                    if len(candidates) <= 0:
                        movies.append(sm)
                    else:
                        candidates.append(sm)
                        merged_movie = merge_movies(candidates)
                        for m in candidates:
                            if m in movies:
                                movies.remove(m)
                        movies.append(merged_movie)

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