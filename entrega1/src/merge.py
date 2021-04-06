import json
import datetime
import unicodedata
from common import Merge, Movie, Show, Scrape, get_movie_id

def normalize(s):
    return s.lower().replace('.','').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')

def test_equal(m1, m2):
    """ 
        testea por igualdad 2 películas
        los criterios de igualdad son:
            al menos un director en común
            al menos un actor en común 
            los títulos idénticos sin tener en cuenta los caracteres especiales.
    """

    """ tiene directores en común (al menos el director principal!!) """
    a1 = [normalize(a) for a in m1[Movie.DIRECTOR.value]]
    a2 = [normalize(a) for a in m2[Movie.DIRECTOR.value]]
    if len(set(a1).intersection(set(a2))) == 0:
        return False

    """ testeo que al menos tenga algun actor en comun (el actor principal!!) """
    a1 = [normalize(a) for a in m1[Movie.ACTORS.value]]
    a2 = [normalize(a) for a in m2[Movie.ACTORS.value]]
    if len(set(a1).intersection(set(a2))) == 0:
        return False

    """ los titulos son iguales sin tener en cuenta los tildes? """
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

    """ uno todos los directores """
    ndirs = []
    directors = []
    for m in ml:
        for a in m[Movie.DIRECTOR.value]:
            ndir = normalize(a)
            if ndir not in ndirs:
                ndirs.append(ndir)
                directors.append(a)                
    
    """ uno los géneros """
    genres = set()
    for m in ml:
        genres.update(m[Movie.GENRE.value])
    genres = list(genres)

    """ duración elijo la mayor """
    duration = -1
    for m in ml:
        duration = m[Movie.DURATION.value] if m[Movie.DURATION.value] > duration else duration

    mr = {
        Movie.TITLE.value: title,
        Movie.ACTORS.value: actors,
        Movie.DIRECTOR.value: directors,
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

    """ uno todos los origenes """
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
    merges = []
    
    for fp in files:
        with open(fp, 'r') as f:
            scraped_data = json.loads(f.read())

            if len(movies) <= 0:
                """ el primer archivo tiene todas las películas unificadas ya """
                movies.extend(sorted(scraped_data[Scrape.MOVIES.value], key=lambda m: m[Movie.DIRECTOR.value]))
            else:
                """ proceso las peliculas scrapeadas y las que ya tengo en movies """
                smovies = sorted(scraped_data[Scrape.MOVIES.value], key=lambda m: m[Movie.DIRECTOR.value])
                for sm in smovies:
                    candidates = [m for m in movies if test_equal(sm, m)]
                    if len(candidates) <= 0:
                        """ la película a procesar no tiene ninguna "igual" en movies """
                        movies.append(sm)
                    else:
                        """ hago merge de las películas ya que la que se está procesando "parece" ser igual a otras almacenadas en movies """
                        candidates.append(sm)
                        merged_movie = merge_movies(candidates)
                        for m in candidates:
                            if m in movies:
                                movies.remove(m)
                        movies.append(merged_movie)

                        candidates_titles = [m[Movie.TITLE.value] for m in candidates]
                        

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