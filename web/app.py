import os

import pandas as pd
from flask import Flask


app = Flask(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/movie_to_rank')
def movie_to_rank():
    movies = pd.read_csv(os.path.join(dir_path, '..', 'data', 'tmdb_5000_movies.csv'))
    return movies.sample(1).iloc[0].to_json()

@app.route('/rank', methods=('POST',))
def rank():
    return ''
