import bs4
import requests
import json
import sys
import re
import datetime


def get_page_and_parse(link):
    r = requests.get(link)
    if not r.ok:
        raise Exception(f'no se pudo obtener el contenido del link {link}')
    return bs4.BeautifulSoup(r.text, 'html.parser')


def process_actors(l):
    return l.split(',')

def process_languaje(l):
    return l.replace('subtitulado', '').replace('subtitulada','').strip()
    
def process_duration(d):
    return d.replace('minutos.','').strip()

process_functions = [
    ('Duracion',process_duration),
    ('Idioma',process_languaje),
    ('Actores',process_actors)
]

def process_data(k,d):
    for pk, pp in process_functions:
        if pk in k:
            return pp(d)    
    return d

def process_movie(movie):
    scraped_data = {}
    titles = movie.find_all('div', attrs={'class':'post-container page-title'})
    title = titles[0].get_text()
    scraped_data['titulo'] = title
    movie_data = movie.find('div', attrs={'class':'page-container singlepost'})

    """ obtengo los datos inciales """
    for d in movie_data.find_all('div', attrs={'class':'dropcap6'}):
        data_type = d.h4.get_text()
        data = d.p.span.get_text()
        processed_data = process_data(data_type, data)
        scraped_data[data_type] = processed_data

    """ obtengo los datos de los horarios - es el último div """
    functions = []
    hours = movie_data.find('div', id=re.compile('Funciones'))

    for function in hours.find_all('div'):
        """ obtener datos del cine y la sala """
        cinema_data = function.h5.span.get_text().split('-')
        cinema = cinema_data[0].strip()
        room = cinema_data[1].strip()
        
        """ obtener datos de las funciones """
        lh = re.compile("(?P<lang>[a-zA-Z]*?):\s*(?P<hours>\d+.*)")
        hs = re.compile("(?P<hours>\d+:\d+)")
        displays = [s.get_text() for s in function.p.find_all('span')]
        for d in displays:
            m1 = lh.match(d)
            language = m1.group('lang')
            hours = m1.group('hours')
            m2 = hs.finditer(hours)
            hours = [h.group('hours') for h in m2]

            functions.append({
                'cine': cinema,
                'sala': room,
                'idioma': language,
                'hours': hours 
            }) 

    scraped_data['funciones'] = functions
    return scraped_data


if __name__ == '__main__':
    base = 'http://cinemalaplata.com.ar/'
    s = get_page_and_parse(f'{base}/?seccion=FUTURO')
    movies = s.find_all('div', attrs={'class':'page-container singlepost'})
    collected_data = []
    for m in movies:
        link = m.find('a').get('href')
        s1 = get_page_and_parse(f"{base}/{link}")
        data = process_movie(s1)
        collected_data.append(data)

    with open(f'data/bruto_cinema_.json','w') as f:
        f.write(json.dumps({'movies':collected_data}, ensure_ascii=False))
