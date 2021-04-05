import bs4
import requests
import json
import sys
import re
import datetime

"""
    ///////////////////////////////
    funciones de normalización 
    //////////////////////
"""


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
        normalized[k] = normalize_data(data)
    return normalized

"""
    ///////////////////
"""


def get_page_and_parse(link):
    r = requests.get(link)
    if not r.ok:
        raise Exception(f'no se pudo obtener el contenido del link {link}')
    return bs4.BeautifulSoup(r.text, 'html.parser')

from merge import Movie, Show

process_functions = [
    (Movie.DURATION.value, lambda s: s.replace('minutos.','').strip()),
    (Movie.LANGUAGE.value, lambda s: s.replace('subtitulado', '').replace('subtitulada','').strip()),
    (Movie.ACTORS.value, lambda l: [s.strip() for s in l.split(',')]),
    (Movie.ORIGIN.value, lambda l: [s.strip() for s in l.split('-')]),
    (Movie.GENRE.value, lambda l: [s.strip() for s in l.split('/')])
]

def process_data(k,d):
    for pk, pp in process_functions:
        if pk is k:
            return pp(d)    
    return d


def process_movie(movie):
    index = {
        'titulo': Movie.TITLE.value,
        'Género': Movie.GENRE.value,
        'Idioma': Movie.LANGUAGE.value,
        'Web Oficial': Movie.WEB.value,
        'Duracion': Movie.DURATION.value,
        'Director': Movie.DIRECTOR.value,
        'Calificacion': Movie.RATING.value,
        'Actores': Movie.ACTORS.value,
        'Origen': Movie.ORIGIN.value
    }

    scraped_data = {}

    """ titulo """
    titles = movie.find_all('div', attrs={'class':'post-container page-title'})
    title = titles[0].get_text()
    scraped_data[Movie.TITLE.value] = title
    movie_data = movie.find('div', attrs={'class':'page-container singlepost'})

    """ 
        obtengo los datos adicionales que tiene la página
    """
    for d in movie_data.find_all('div', attrs={'class':'dropcap6'}):
        data_type = normalize_data(d.h4.get_text())
        normalized_key = index[data_type]
        data = d.p.span.get_text()
        processed_data = process_data(normalized_key, data)
        scraped_data[normalized_key] = processed_data

    """ obtengo los datos de los horarios - es el último div """
    functions = []
    hours = movie_data.find('div', id=re.compile('Funciones'))

    for function in hours.find_all('div'):
        """ obtener datos del cine y la sala """
        cinema_data = function.h5.span.get_text().split('-')
        cinema = cinema_data[0].strip()
        room = cinema_data[1].strip()
        
        """ obtener datos de las funciones """
        rlang_hours = re.compile("(?P<lang>[a-zA-Z]*?):\s*(?P<hours>\d+.*)")
        rhours = re.compile("(?P<hours>\d+:\d+)")
        displays = [s.get_text() for s in function.p.find_all('span')]
        for d in displays:
            m1 = rlang_hours.match(d)
            language = m1.group('lang')
            hours = m1.group('hours')
            m2 = rhours.finditer(hours)
            hours = [h.group('hours') for h in m2]

            functions.append({
                Show.CINEMA.value: cinema,
                Show.SHOWROOM.value: room,
                Show.LANGUAGE.value: language,
                Show.HOURS.value: hours 
            }) 

    scraped_data[Movie.SHOWS.value] = functions
    return scraped_data


if __name__ == '__main__':
    base = 'http://cinemalaplata.com.ar/'
    s = get_page_and_parse(f'{base}/Cartelera.aspx')
    movies = s.find_all('div', attrs={'class':'page-container singlepost'})
    collected_data = []
    for m in movies:
        link = m.find('a').get('href')
        s1 = get_page_and_parse(f"{base}/{link}")
        data = process_movie(s1)
        ndata = normalize_dict(data)
        collected_data.append(ndata)

    with open(f'data/scraper_cinema.json','w') as f:
        f.write(json.dumps({'movies':collected_data}, ensure_ascii=False))
