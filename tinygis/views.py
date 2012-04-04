import random
import string
import flask
from path import path as ppath
from sqlitedict import SqliteDict
import polygons
import auth


tinygis = flask.Blueprint('tinygis', __name__,
                          template_folder='templates',
                          static_folder='static')


@tinygis.route('/')
def index():
    return flask.render_template('map.html')


@tinygis.route('/get_features_at')
def get_features_at():
    lat = float(flask.request.args.get('lat', float))
    lng = float(flask.request.args.get('lng', float))
    return flask.jsonify({
        'hit_list': list(polygons.features_at({'lat': lat, 'lng': lng})),
    })


def _get_db():
    return flask.current_app.extensions['tinygis-db']


def _random_id(length=6, exists=lambda new_id: False):
    vocabulary = string.ascii_letters + string.digits
    for c in xrange(100):
        new_id = ''.join(random.choice(vocabulary) for c in xrange(length))
        if not exists(new_id):
            return new_id
    else:
        raise ValueError("Random ID generator giving up after 100 attempts")


@tinygis.route('/userlayers', methods=['POST'])
@auth.require_login
def userlayer_create():
    db = _get_db()
    key = _random_id(exists=lambda new_id: (new_id + '.meta') in db)
    db[key + '.meta'] = {
        'owner': flask.g.user_id,
    }
    db[key + '.geojson'] = flask.json.dumps(flask.request.json, indent=2)
    return flask.jsonify({'id': key})


@tinygis.route('/userlayers/<string:key>', methods=['PUT'])
@auth.require_login
def userlayer_update(key):
    db = _get_db()
    try:
        meta = db[key + '.meta']
    except KeyError:
        flask.abort(404)
    if meta['owner'] != flask.g.user_id:
        flask.abort(403)
    db[key + '.geojson'] = flask.json.dumps(flask.request.json, indent=2)
    return flask.jsonify({})


@tinygis.route('/userlayers/<string:key>', methods=['GET'])
@auth.require_login
def userlayer_get(key):
    db = _get_db()
    try:
        meta = db[key + '.meta']
    except KeyError:
        flask.abort(404)
    if meta['owner'] != flask.g.user_id:
        flask.abort(403)
    return flask.Response(db[key + '.geojson'], mimetype='application/json')


def register(app, url_prefix='/map'):
    app.register_blueprint(tinygis, url_prefix=url_prefix)
    db = SqliteDict(ppath(app.instance_path)/'tinygis.db', autocommit=True)
    app.extensions['tinygis-db'] = db
