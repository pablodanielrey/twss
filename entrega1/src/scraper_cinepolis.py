import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""
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
"""



def ec_movies():
    return EC.presence_of_element_located((By.CLASS_NAME,'movie-grid'))

def movie_details():
    return EC.presence_of_element_located((By.CLASS_NAME,'movie-detail-showtimes-component'))

def movie_filters():
    return EC.presence_of_element_located((By.CLASS_NAME,'showtimes-filter-component'))

def movie_dates_filter():
    return EC.presence_of_element_located((By.CLASS_NAME,'showtimes-filter-component-dates'))

def movie_showtimes_data():
    return EC.presence_of_element_located((By.CLASS_NAME,'accordion'))


def wait_until_loaded(driver, ec):
    element = WebDriverWait(driver, 10).until(ec())
    return element

if __name__ == '__main__':

    base = 'https://www.cinepolis.com.ar'

    driver = webdriver.Chrome()
    driver.get(base)
    
    buttons = driver.find_elements_by_tag_name('button')
    for b in buttons:
        if 'Ver todo' == b.text:
            print('apretando botón')
            b.click()

    print('esperando el resultado')
    movies = wait_until_loaded(driver, ec_movies)
    print('resultado obtenido')
    hrefs = [a.get_attribute('href') for a in movies.find_elements_by_tag_name('a')]

    for href in hrefs:
        driver.get(href)
        details = wait_until_loaded(driver, movie_details)
        filters = wait_until_loaded(details, movie_filters)

        """
            Selecciono el Todos de cada filtro.
            lo hago explícito para que quede mas claro el código
        """
        filters_to_select = ['showtimes-filter-component-screens', 'showtimes-filter-component-formats', 'showtimes-filter-component-versions']
        for fs in filters_to_select:
            selected_filter = filters.find_element_by_class_name(fs)
            try:
                todos = [b for b in selected_filter.find_elements_by_tag_name('button') if b.text == 'Todos'][0]
                print('Seleccionando filtro Todos')
                todos.click()
                print('Esperando resultados')
                wait_until_loaded(details, movie_showtimes_data)
            except Exception as e:
                print('No debería haber pasado ya que siempre existe el Todos en los filtros')
                print(e)


        """
            voy seleccionando por día disponible
        """
        dates_filter = filters.find_element_by_class_name('showtimes-filter-component-dates')
        try:
            for day in dates_filter.find_elements_by_tag_name('button'):
                date = day.get_attribute('value')
                print(f'Cargando resultados para fecha {date}')
                day.click()
                print('Espernado los resultados')
                wait_until_loaded(details, movie_showtimes_data)
        except Exception as e:
            print(e)

        print('esperando que esten los resultados cargados')
        wait_until_loaded(details, movie_showtimes_data)
        print(details.text)

    """
    cplx = driver.find_element_by_id("complex_id_select")
    elem.clear()  
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)
    assert "No results found." not in driver.page_source
    """
    driver.close()
