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
        scraped_data[data_type] = data

    """ obtengo los datos de los horarios - es el último div """
    functions = []
    hours = movie_data.find('div', id=re.compile('Funciones'))

    for function in hours.find_all('div'):
        cinema = function.h5.span.get_text()
        displays = [s.get_text() for s in function.p.find_all('span')]
        functions.append({
            'cine': cinema,
            'shows': displays
        }) 

    scraped_data['funciones'] = functions
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
        collected_data.append(data)

    with open(f'data/bruto_cinema_.json','w') as f:
        f.write(json.dumps({'movies':collected_data}, ensure_ascii=False))
