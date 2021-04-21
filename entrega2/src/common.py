

def get_urls_of_data() -> list:
    urls = [
        'https://www.ecartelera.com/peliculas/wonder-woman-1984',
        'https://www.rottentomatoes.com/m/wonder_woman_1984',
        'https://www.metacritic.com/movie/wonder-woman-1984',
        'https://www.imdb.com/title/tt7126948/'
    ]
    return urls

def get_file_name(url:str) -> str:
    return url.split('.')[1]