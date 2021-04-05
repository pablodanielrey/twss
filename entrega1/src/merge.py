

"""
    Registro de claves.

    Movies:
        title
        original_title
        genre
        language
        web
        origin
        duration
        director
        rating
        actors
        distribution
        synopsis

    Shows:
        cinema
        showroom
        format
        language
        subtitles = True|False
        hours:
            xx:xx
            xx:xx
            xx:xx


"""
from enum import Enum
class Movie(Enum):
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
    CINEMA = 'CINEMA'
    SHOWROOM = 'SHOWROOM'
    LANGUAGE = 'LANGUAGE'
    HOURS = 'HOURS'
    FORMAT = 'FORMAT'

    