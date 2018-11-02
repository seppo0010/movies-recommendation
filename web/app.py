import os
from uuid import uuid4

import pandas as pd
from flask import Flask, request, make_response

from recommendation import prepare_df, train_model, load_model


app = Flask(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(dir_path, '..', 'data')
movies = pd.read_csv(os.path.join(data_dir, 'tmdb_5000_movies.csv')).set_index('id')
prepared_movies = pd.read_csv(os.path.join(data_dir, 'prepared.csv')).set_index('id')
GOOD = 'g'
BAD = 'b'
SKIP = 's'


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
    rated = labels[(labels['label'] == GOOD) | (labels['label'] == BAD)]
    joined = movies.join(labels, how='left')
    row = joined[pd.isna(joined['label'])].nlargest(100, 'popularity').sample(1).reset_index().iloc[0]
    model_path = os.path.join(data_dir, session + '.model')
    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as fp:
                model = load_model(fp.read())
            row['prediction'] = model['model'].predict_proba(prepare_df(pd.DataFrame([row])))[0,1]
            row['accuracy'] = model['test_accuracy'].mean()
        except EOFError:
            os.unlink(model_path)
    row['num_rated'] = rated.shape[0]
    row['num_skipped'] = labels[labels['label'] == SKIP].shape[0]
    return row.to_json()


@app.route('/rank', methods=('POST',))
def rank():
    session = request.cookies.get('session', None)
    if session is None:
        raise Exception('No session found')
    content = request.get_json(silent=True)
    if not isinstance(content['id'], int):
        return 'invalid id', 400
    if content.get('value', '')[:1] not in (GOOD, BAD, SKIP):
        return 'invalid value', 400

    session_path = os.path.join(data_dir, session)
    with open(session_path, 'a') as fp:
        fp.write('{},{}\n'.format(content['id'], content['value'][0]))

    if content['value'][:1] != SKIP:
        labels = pd.read_csv(os.path.join(data_dir, session)).set_index('id')
        good = labels[labels['label'] == GOOD].shape[0]
        bad = labels[labels['label'] == BAD].shape[0]
        rated = good + bad
        if rated > 9 and rated % 1 == 0 and good > 4 and bad > 4:
            with open(os.path.join(data_dir, session + '.model'), 'wb') as fp:
                fp.write(train_model(labels.join(prepared_movies)))
    return ''
