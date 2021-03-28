import bs4
import requests


def get_page_and_parse(link):
    r = requests.get(link)
    if not r.ok:
        raise Exception(f'no se pudo obtener el contenido del link {link}')
    return bs4.BeautifulSoup(r.text, 'html.parser')

if __name__ == '__main__':
    base = 'http://cinemalaplata.com.ar/'
    s = get_page_and_parse(f'{base}/Cartelera.aspx')
    movies = s.find_all('div', attrs={'class':'page-container singlepost'})
    for m in movies:
        link = m.find('a').get('href')
        s1 = get_page_and_parse(f"{base}/{link}")
        print(s1)