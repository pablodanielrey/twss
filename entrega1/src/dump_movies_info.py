"""
    script utilitario para hacer un json con info plana sobre cada película.
    solo para proceso de debug y verificación
    procesa el archivo de merge
"""

import json
import datetime
from common import Merge, MergeInfo, Movie, Show

if __name__ == '__main__':

    movies = []
    with open('data/merged.json', 'r') as f:
        merges = json.loads(f.read())
        _movies = merges[Merge.MOVIES.value]
        for m in _movies:
            m['SHOWS'] = [s for s in merges[Merge.SHOWS.value] if s[Show.MOVIE.value] == m[Movie.ID.value]]
            m['MERGES'] = [s[MergeInfo.MOVIES.value] for s in merges[Merge.MERGES.value] if s[MergeInfo.NEW_ID.value] == m[Movie.ID.value]]
            movies.append(m)

    dumped = {
        'DATE': str(datetime.datetime.utcnow()),
        'MOVIES': movies
    }

    with open('data/dumped.json', 'w') as f:
        f.write(json.dumps(dumped, ensure_ascii=False))