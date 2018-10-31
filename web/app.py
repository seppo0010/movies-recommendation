import os
from uuid import uuid4

import pandas as pd
from flask import Flask, request, make_response


app = Flask(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(dir_path, '..', 'data')
movies = pd.read_csv(os.path.join(data_dir, 'tmdb_5000_movies.csv')).set_index('id')


@app.route('/')
def root():
    resp = make_response(app.send_static_file('index.html'))
    if request.cookies.get('session', None) is None:
        resp.set_cookie('session', str(uuid4()))
    return resp


@app.route('/movie_to_rank')
def movie_to_rank():
    session = request.cookies.get('session', None)
    if session is None:
        raise Exception('No session found')
    session_path = os.path.join(data_dir, session)
    if not os.path.exists(session_path):
        with open(session_path, 'w') as fp:
            fp.write('id,label\n')
    labels = pd.read_csv(os.path.join(data_dir, session)).set_index('id')
    row = movies.join(labels, how='left').sample(1).reset_index().iloc[0]
    row['num_rated'] = labels.shape[0]
    return row.to_json()


@app.route('/rank', methods=('POST',))
def rank():
    session = request.cookies.get('session', None)
    if session is None:
        raise Exception('No session found')
    content = request.get_json(silent=True)
    if not isinstance(content['id'], int):
        return 'invalid id', 400
    if content.get('value', None) not in ('good', 'bad', 'skip'):
        return 'invalid value', 400

    session_path = os.path.join(data_dir, session)
    with open(session_path, 'a') as fp:
        fp.write('{},{}\n'.format(content['id'], content['value'][0]))
    return ''
