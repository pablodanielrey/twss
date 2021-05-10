import sys
import uuid
import json
from urllib.parse import quote

from rdflib import Graph, RDF, RDFS, Namespace, Literal
from rdflib.term import URIRef


def load_data():
    with open('data/merged_tp1.json') as f:
        data = json.loads(f.read())
    return data


def get_ontology():
    o = Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/twss_simple.ttl#')
    d = Namespace('https://raw.githubusercontent.com/pablodanielrey/twss/master/owl/data/')
    return (o,d)

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


if __name__ == '__main__':

    o,d = get_ontology()
    g = Graph()
    g.bind("twss", o)
    g.bind("twssd", d)

    persons_map = {}
    movie_map = {}
    cinema_map = {}
    showroom_map = {}

    ''' agrego las películas dentro del grafo '''
    data = load_data()
    for movie in data['MOVIES']:
        iri = get_movie_iri(movie_map, movie)
        dmovie = d[iri]

        g.add((dmovie, RDF.type, o.Movie))

        if 'LANGUAGE' in movie:
            g.add((dmovie, o.language, Literal(movie['LANGUAGE'])))

        g.add((dmovie, o.durationInMinutes, Literal(movie['DURATION'])))
        g.add((dmovie, o.synopsis, Literal(movie['SYNOPSIS'])))
        g.add((dmovie, o.movieRating, Literal(movie['RATING'])))
        if 'WEB' in movie and movie['WEB'] != 'No disponible':
            g.add((dmovie, RDFS.seeAlso, Literal(movie['WEB'])))

        g.add((dmovie, o.title, Literal(movie['TITLE'])))
        if 'ORIGINAL_TITLE' in movie:
            g.add((dmovie, o.title, Literal(movie['ORIGINAL_TITLE'])))
        
        for genre in movie['GENRE']:
            g.add((dmovie, o.genre, Literal(genre)))

        for co in movie['ORIGIN']:
            g.add((dmovie, o.countryOfOrigin, Literal(co)))

        for director in movie['DIRECTOR']:
            piri = get_person_iri(persons_map, director)
            g.add((dmovie, o.director, d[piri]))

        for actor in movie['ACTORS']:
            piri = get_person_iri(persons_map, actor)
            g.add((dmovie, o.actor, d[piri]))


    ''' agrego los actores identificados dentro del grafo '''
    for name, iri in persons_map.items():
        piri = d[iri]
        g.add((piri, RDF.type, o.Person))
        g.add((piri, o.name, Literal(name)))

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
        ''' pelicula '''
        g.add((shiri, o.movie, d[miri]))
        ''' sala '''
        g.add((shiri, o.showsIn, showroom_iri))
        ''' lenguaje de reproducción '''
        g.add((shiri, o.showLanguage, Literal(show['LANGUAGE'])))
        ''' formato de reproduccion '''
        if 'FORMAT' in show:
            g.add((shiri, o.showFormat, Literal(show['FORMAT'])))         

        for hour in show['HOURS']:
            ''' hora de reproducción '''
            g.add((shiri, o.showTime, Literal(hour)))
        
    ''' agrego las salas y los cines '''
    for showroom in showroom_map:
        shiri = d[showroom_map[showroom]['IRI']]
        ciri = d[showroom_map[showroom]['CINEMA']]
        g.add((shiri, RDF.type, o.ShowRoom))
        g.add((shiri, o.name, Literal(showroom_map[showroom]['SHOWROOM'])))
        g.add((shiri, o.isPartOf, ciri))
    
    ''' agrego los cines '''
    for cinema_name in cinema_map:
        ciri = d[cinema_map[cinema_name]]
        g.add((ciri, RDF.type, o.Cinema))
        g.add((ciri, o.name, Literal(cinema_name)))

    ''' escribo todos los datos '''
    with open('data/tp1.ttl','w') as f:
        f.write(g.serialize(format="turtle").decode("utf-8"))

    with open('data/tp1_persons.ttl', 'w') as f:
        g2 = Graph()
        g2.bind("twss", o)
        g2.bind("twssd", d)        
        for t in g.triples((None, RDF.type, o.Person)):
            for t2 in g.triples((t[0],None,None)):
                g2.add(t2)
        f.write(g2.serialize(format="turtle").decode("utf-8"))

    with open('data/tp1_showrooms.ttl', 'w') as f:
        g2 = Graph()
        g2.bind("twss", o)
        g2.bind("twssd", d)        
        for t in g.triples((None, RDF.type, o.ShowRoom)):
            for t2 in g.triples((t[0],None,None)):
                g2.add(t2)
        f.write(g2.serialize(format="turtle").decode("utf-8"))

    with open('data/tp1_cinemas.ttl', 'w') as f:
        g2 = Graph()
        g2.bind("twss", o)
        g2.bind("twssd", d)        
        for t in g.triples((None, RDF.type, o.Cinema)):
            for t2 in g.triples((t[0],None,None)):
                g2.add(t2)
        f.write(g2.serialize(format="turtle").decode("utf-8"))

