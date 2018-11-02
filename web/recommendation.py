import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate
import pickle

genres = [
    'action',
    'adventure',
    'animation',
    'comedy',
    'crime',
    'documentary',
    'drama',
    'family',
    'fantasy',
    'foreign',
    'history',
    'horror',
    'music',
    'mystery',
    'romance',
    'science fiction',
    'thriller',
    'tv movie',
    'war',
    'western',
]

keywords = [
    'woman director',
    'independent film',
    'duringcreditsstinger',
    'based on novel',
    'murder',
    'aftercreditsstinger',
    'violence',
    'dystopia',
    'sport',
    'revenge',
    'sex',
    'friendship',
    'biography',
    'musical',
    'teenager',
    '3d',
    'love',
    'sequel',
    'suspense',
    'new york',
    'police',
    'los angeles',
    'high school',
    'alien',
    'prison',
    'nudity',
    'drug',
    'family',
    'london england',
    'superhero',
    'dying and death',
    'father son relationship',
    'daughter',
    'world war ii',
    'kidnapping',
    'wedding',
    'remake',
    'serial killer',
    'suicide',
    'magic',
    'friends',
    'corruption',
    'based on comic book',
    'escape',
    'hospital',
    'party',
    'based on true story',
    'martial arts',
    'time travel',
    'airplane',
    'investigation',
    'brother brother relationship',
    'fbi',
    'female nudity',
    'survival',
    'blood',
    'money',
    'fight',
    'future',
    'best friend',
    'cia',
    'gay',
    'music',
    'secret',
    'lawyer',
    "love of one's life",
    'paris',
    'zombie',
    'flashback',
    'small town',
    'undercover',
    'war',
    'based on young adult novel',
    'explosion',
    'new love',
    'assassin',
    'conspiracy',
    'death',
    'jealousy',
    'rape',
    'rescue',
    'vampire',
    'wife husband relationship',
    'witch',
    'divorce',
    'journalist',
    'prostitute',
    'shootout',
    'monster',
    'obsession',
    'robbery',
    'spy',
    'teacher',
    'detective',
    'dog',
    'england',
    'gore',
    'hotel',
    'new york city',
    'soldier'
]

production_companies =  [
    'warner bros.',
    'universal pictures',
    'paramount pictures',
    'twentieth century fox film corporation',
    'columbia pictures',
    'new line cinema',
    'metro-goldwyn-mayer (mgm)',
    'touchstone pictures',
    'walt disney pictures',
    'relativity media',
]

production_countries = [
    'united states of america',
    'united kingdom',
    'germany',
    'france',
    'canada',
    'australia',
    'italy',
    'spain',
]
spoken_languages = [
    'english',
    'français',
    'español',
    'deutsch',
    'italiano',
    'Pусский'.lower(),
    '普通话'.lower(),
]

raw_fields = ['budget', 'popularity', 'revenue', 'runtime', 'vote_average', 'vote_count']
# release_date

def prepare_df(df):
    def open_properties(df, field, keys):
        def do_open(s):
            my_fields = set(map(lambda x: x['name'].lower(), json.loads(s)))
            return pd.Series([int(g in my_fields) for g in keys], index=keys)
        df[keys] = df[field].apply(do_open)

    open_properties(df, 'genres', genres)
    open_properties(df, 'keywords', keywords)
    open_properties(df, 'production_companies', production_companies)
    open_properties(df, 'production_countries', production_countries)
    open_properties(df, 'spoken_languages', spoken_languages)
    return df[['id'] + genres + keywords + production_companies + production_countries + spoken_languages + raw_fields]


def train_model(df):
    df['label'] = df['label'].apply(lambda x: int(x == 'g'))
    y = df['label']
    X = df.drop(['label'], axis=1)
    clf = RandomForestClassifier(class_weight='balanced', random_state=0, n_estimators=50)
    result = cross_validate(clf, X, y, scoring=['accuracy'], return_train_score=False)
    clf.fit(X, y)
    result['model'] = clf
    return pickle.dumps(result)


load_model = pickle.loads


if __name__ == '__main__':
    df = pd.read_csv('../data/tmdb_5000_movies.csv')
    prepare_df(df).to_csv('../data/prepared.csv')
