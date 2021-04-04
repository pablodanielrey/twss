"""
    scraper de cinépolis.com.ar

    Notas:
        La página ya carga la cartelera con todas las películas así que no es necesario interactuar con los filtros de la misma
        En el detalle de la película hace lo mismo. carga la info completa, por lo que no es necesario interactuar tampoco con los filtros para obtener todas las funciones.

    estructura básica de la info de la película dentro de la página

    moview-detail-showtimes-component
            showtimes-filter-component
                showtimes-filter-component-screens
                showtimes-filter-component-formats
                showtimes-filter-component-versions
                showtimes-filter-component-dates
                    ul
                        li
                            button <-- value = 2021-04-03
                        li
                            button <-- value = 2021-04-04
            accordion
                movie-showtimes-component
                    movie-showtimes-component-combination
                        movie-showtimes-component-label
                        movie-showtimes-component-schedule

"""


import time
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


"""
    ///////////////////////////
    funciones de normalización
    ///////////////////////////
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
        normalized[normalize_data(k)] = normalize_data(data)
    return normalized


def list_normalizer(d):
    return [s.strip() for s in d.split(',')]

matrix_normalizer = [
    ('Origen',list_normalizer),
    ('Género', list_normalizer),
    ('Actores', list_normalizer),
    ('Duración', lambda s: s.replace('min.','').strip())
]

"""
    ////////////////////////
"""


def ec_movies():
    return EC.presence_of_element_located((By.CLASS_NAME,'movie-grid'))

def movie_show_data():
    return EC.presence_of_element_located((By.CLASS_NAME,'accordion'))

def movie_filters():
    return EC.presence_of_element_located((By.CLASS_NAME,'showtimes-filter-component'))




def movie_details():
    return EC.presence_of_element_located((By.CLASS_NAME,'movie-detail-showtimes-component'))


def movie_dates_filter():
    return EC.presence_of_element_located((By.CLASS_NAME,'showtimes-filter-component-dates'))

def movie_showtimes_data():
    return EC.presence_of_element_located((By.CLASS_NAME,'movie-showtimes-component'))


def wait_until_loaded(driver, ec):
    element = WebDriverWait(driver, 10).until(ec())
    return element


def scrape_movie_data(driver):
    movie = {}
    title_element = driver.find_element_by_xpath("/html/body/div/main/div[1]/div/h2")
    movie['Título'] = title_element.get_attribute('textContent').strip()
    md = driver.find_element_by_xpath("//div[@id='tecnicos']/p")
    mdt = md.get_attribute('innerHTML').split('<br>')
    for m in mdt:
        mdata = m.replace('<strong>','').replace('</strong>','').replace('<br>','').replace('\n','').strip().split(':')
        if len(mdata) > 1:
            key = mdata[0]
            data = mdata[1]
            for nk, nf in matrix_normalizer:
                if key == nk:
                    movie[key] = nf(data)
                    break
            else:
                movie[key] = data
    return movie

def scrape_movie_shows_data(driver):
    """
        obtiene los datos de las funciones para una fecha ya cargada
    """
    movie_shows = []

    #all_cinemas = driver.find_elements_by_class_name('panel-primary')
    all_cinemas = driver.find_elements_by_xpath(".//div[contains(@class,'panel-primary')]")
    for cinema in all_cinemas:
        data = {}

        cinema_name = cinema.find_element_by_xpath('.//div[1]/h2/button')
        data['cine'] = cinema_name.text

        shows = cinema.find_elements_by_class_name('movie-showtimes-component-combination')
        for show in shows:

            show_formats = show.find_element_by_xpath("//div[contains(@class,'movie-showtimes-component-label')]/div/small")
            room_data = show_formats.get_attribute('innerHTML')
            rfi = room_data.split('•')
            data['sala'] = rfi[0]
            data['formato'] = rfi[1]
            data['idioma'] = rfi[2]

            schedule = show.find_element_by_xpath("//div[contains(@class,'movie-showtimes-component-schedule')]")
            hours = schedule.find_elements_by_tag_name('a')
            hp = [h.get_attribute('innerHTML') for h in hours]
            data['hours'] = hp

        nd = normalize_data(data)
        movie_shows.append(nd)
    
    return movie_shows


if __name__ == '__main__':

    movies_data = []


    base = 'https://www.cinepolis.com.ar'

    driver = webdriver.Chrome()
    driver.get(base)
    
    buttons = driver.find_elements_by_tag_name('button')
    for b in buttons:
        if 'Ver todo' == b.text:
            print('apretando botón')
            b.click()

    """
        Por defecto cuando se carga la página se ven todas las películas. asi que no es necesario interactuar con el botón de filtro.
        me aseguro de que esté cargada la página con los datos de las películas que necesito.
    """
    movies = wait_until_loaded(driver, ec_movies)
    hrefs = [a.get_attribute('href') for a in movies.find_elements_by_tag_name('a')]

    for href in hrefs:
        driver.get(href)
        
        """
            /////////////////////////////////////////////////
            scrapping de los dátos básicos de la película 
            /////////////////////////////////////////////////
        """
        
        movie_data = scrape_movie_data(driver)


        """
            ////////////////////////////////////////////////
            scrapping teniendo en cuenta los filtros
            por defecto quedan seleccionados los que necesito:
            salas = Todas
            formato = Todos
            idioma = Todos
            día = Hoy
            así que no es necesario que interactúe con ninguno de los filtros. en la version v1 del scrapper se encuentra el código para seleccionar cada uno y scrapear por todos los días.
            ///////////////////////////////////////////////
        """

        """
            selecciono el primer día, que en la página es el día actual
        """
        """
        filters = wait_until_loaded(driver, movie_filters)
        dates_filter = filters.find_element_by_class_name('showtimes-filter-component-dates')
        day = dates_filter.find_elements_by_tag_name('button')[0]
        day.click()
        """

        details = wait_until_loaded(driver, movie_show_data)
        movie_data['funciones'] = scrape_movie_shows_data(details)
        movies_data.append(movie_data)

    driver.close()

    with open(f'data/scraper_cinepolis.json','w') as f:
        f.write(json.dumps({'movies':movies_data}, ensure_ascii=False))

