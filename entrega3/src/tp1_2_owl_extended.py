import sys
import uuid
import json
from urllib.parse import quote

from rdflib import Graph, RDF, RDFS, OWL, Namespace, Literal
from rdflib.term import URIRef


def load_data():
    with open('data/tp1/merged_tp1.json') as f:
        data = json.loads(f.read())
    return data


def get_ontology():
    s = Namespace('http://schema.org/')
    o = Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_schema_extended.ttl#')
    d = Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/data/')
    return (s, o,d)

def bind_schemas(g:Graph):
    s,o,d = get_ontology()
    g.bind('schema',s)
    g.bind("twsss", o)
    g.bind("twssd", d)

def get_movie_iri(movie_map, movie):
    if movie['ID'] in movie_map:
        return movie_map['ID']

    if 'ORIGINAL_TITLE' in movie:
        title = movie['ORIGINAL_TITLE']
    else:
        title = movie['TITLE']
    iri = quote(title.replace(' ','_'))
    movie_map[movie['ID']] = iri
    return iri

def get_person_iri(persons_map, person):
    person = person.replace('.','')
    if person in persons_map:
        return persons_map[person]
    iri = quote(person.replace(' ','_'))
    persons_map[person] = iri
    return iri

def get_showrom_iris(cinema_map, showroom_map, show):
    cinema = show['CINEMA']
    if cinema in cinema_map:
        ciri = cinema_map[cinema]
    else:
        ciri = quote(cinema.replace(' ', '_'))
        cinema_map[cinema] = ciri

    showroom = f"{show['CINEMA']}_{show['SHOWROOM']}"
    if showroom in showroom_map:
        return (ciri, showroom_map[showroom]['IRI'])
    iri = f'showroom_{str(uuid.uuid4())}'
    showroom_map[showroom] = {
        'IRI': iri,
        'CINEMA': ciri,
        'SHOWROOM': show['SHOWROOM']
    }
    return (ciri, iri)


def find_movie_by_id(movies, movie_id):
    for m in movies:
        if m['ID'] == movie_id:
            return m
    return None

if __name__ == '__main__':

    s, o, d = get_ontology()
    g = Graph()
    bind_schemas(g)

    persons_map = {}
    movie_map = {}
    cinema_map = {}
    showroom_map = {}

    ''' agrego las películas dentro del grafo '''
    print(f'Cargando datos del tp1')
    data = load_data()
    for movie in data['MOVIES']:
        print(f"Procesando película : {movie['TITLE']}")
        iri = get_movie_iri(movie_map, movie)
        dmovie = d[iri]

        g.add((dmovie, RDF.type, s.Movie))
        g.add((dmovie, RDF.type, OWL.NamedIndividual))

        if 'LANGUAGE' in movie:
            g.add((dmovie, s.inLanguage, Literal(movie['LANGUAGE'])))

        g.add((dmovie, s.duration, Literal(movie['DURATION'])))
        g.add((dmovie, s.text, Literal(movie['SYNOPSIS'])))
        g.add((dmovie, s.contentRating, Literal(movie['RATING'])))
        if 'WEB' in movie and movie['WEB'] != 'No disponible':
            g.add((dmovie, RDFS.seeAlso, Literal(movie['WEB'])))

        g.add((dmovie, s.name, Literal(movie['TITLE'])))
        if 'ORIGINAL_TITLE' in movie:
            g.add((dmovie, s.name, Literal(movie['ORIGINAL_TITLE'])))
        
        for genre in movie['GENRE']:
            g.add((dmovie, s.genre, Literal(genre)))

        for co in movie['ORIGIN']:
            g.add((dmovie, s.countryOfOrigin, Literal(co)))

        for director in movie['DIRECTOR']:
            piri = get_person_iri(persons_map, director)
            g.add((dmovie, s.director, d[piri]))

        for actor in movie['ACTORS']:
            piri = get_person_iri(persons_map, actor)
            g.add((dmovie, s.actor, d[piri]))


    ''' agrego los actores identificados dentro del grafo '''
    for name, iri in persons_map.items():
        piri = d[iri]
        g.add((piri, RDF.type, s.Person))
        g.add((piri, RDF.type, OWL.NamedIndividual))
        g.add((piri, s.name, Literal(name)))

    ''' agrego los datos de los shows '''
    for show in data['SHOWS']:
        movie_id = show['MOVIE']
        miri = movie_map[movie_id]

        ciri, siri = get_showrom_iris(cinema_map, showroom_map, show)
        showroom_iri = d[siri]

        ''' el iri del show es autogenerado '''
        show_iri = f'show_{str(uuid.uuid4())}'
        shiri = d[show_iri]

        g.add((shiri, RDF.type, o.Show))
        g.add((shiri, RDF.type, OWL.NamedIndividual))
        ''' pelicula '''
        g.add((shiri, o.movie, d[miri]))
        ''' sala '''
        g.add((shiri, o.showRoom, showroom_iri))
        ''' lenguaje de reproducción '''

        if 'Subtitulado' in show['LANGUAGE']:
            _movie = find_movie_by_id(data['MOVIES'], show['MOVIE'])
            if 'LANGUAGE' in _movie:
                g.add((shiri, s.inLanguage, Literal(_movie['LANGUAGE'])))
        ''' formato de reproduccion '''
        if 'FORMAT' in show:
            g.add((shiri, o.movieFormat, Literal(show['FORMAT'])))         

        for hour in show['HOURS']:
            ''' hora de reproducción '''
            g.add((shiri, s.startDate, Literal(hour)))
        
    ''' agrego las salas y los cines '''
    for showroom in showroom_map:
        shiri = d[showroom_map[showroom]['IRI']]
        ciri = d[showroom_map[showroom]['CINEMA']]
        g.add((shiri, RDF.type, o.ShowRoom))
        g.add((shiri, RDF.type, OWL.NamedIndividual))
        g.add((shiri, s.name, Literal(showroom_map[showroom]['SHOWROOM'])))
        g.add((shiri, o.cinema, ciri))
    
    ''' agrego los cines '''
    for cinema_name in cinema_map:
        ciri = d[cinema_map[cinema_name]]
        g.add((ciri, RDF.type, o.Cinema))
        g.add((ciri, RDF.type, OWL.NamedIndividual))
        g.add((ciri, s.name, Literal(cinema_name)))


    ''' busco la ontología definida en protegé y le hago merge con los datos de los individuals arriba procesados '''
    gontology = Graph()
    with open('../owl/twss_schema_extended.ttl', 'r') as f:
        gontology.parse(f, format='turtle')


    gfinal = gontology + g

    ''' escribo todos los datos '''
    with open('data/merged_tp1_extended.ttl','w') as f:
        f.write(gfinal.serialize(format="turtle").decode("utf-8"))


