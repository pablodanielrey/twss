

from enum import Enum

class Merge(Enum):
    DATE = 'DATE'
    MOVIES = 'MOVIES'
    SHOWS = 'SHOWS'

class Scrape(Enum):
    DATE = 'DATE'
    SOURCE = 'SOURCE'
    MOVIES = 'MOVIES'
    SHOWS = 'SHOWS'
    VALIDITY = 'VALIDITY'

class Movie(Enum):
    ID = 'ID'
    TITLE = 'TITLE'
    ORIGINAL_TITLE = 'ORIGINAL_TITLE'
    GENRE = 'GENRE'
    LANGUAGE = 'LANGUAGE'
    WEB = 'WEB'
    ORIGIN = 'ORIGIN'
    DURATION = 'DURATION'
    DIRECTOR = 'DIRECTOR'
    ACTORS = 'ACTORS'
    RATING = 'RATING'
    DISTRIBUTION = 'DISTRIBUTION'
    SYNOPSIS = 'SYNOPSIS'
    SHOWS = 'SHOWS'

class Show(Enum):
    MOVIE = 'MOVIE'
    CINEMA = 'CINEMA'
    SHOWROOM = 'SHOWROOM'
    LANGUAGE = 'LANGUAGE'
    HOURS = 'HOURS'
    FORMAT = 'FORMAT'


def get_movie_id(movie):
    return movie[Movie.TITLE.value]