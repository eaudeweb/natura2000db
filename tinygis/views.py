# encoding: utf-8
import random
import string
import flask
from path import path
from sqlitedict import SqliteDict
import polygons
import auth


tinygis = flask.Blueprint('tinygis', __name__,
                          template_folder='templates',
                          static_folder='static')


@tinygis.route('/')
def index():
    return flask.render_template('map.html')


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


@tinygis.route('/userlayers', methods=['GET'])
def userlayer_list():
    db = _get_db()
    key_list = []
    for db_key in db:
        if not db_key.endswith('.meta'):
            continue
        key = db_key.rsplit('.', 1)[0]
        meta = db[key + '.meta']
        if meta['owner'] != flask.g.user_id:
            continue
        key_list.append(key)
    return flask.jsonify({'ids': key_list})


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


@tinygis.route('/get_features_at')
def get_features_at():
    latlng = {
        'lat': float(flask.request.args.get('lat', float)),
        'lng': float(flask.request.args.get('lng', float)),
    }
    return flask.jsonify({
        'hit_list': [{'layer': l.name, 'feature_name': f['properties']['name']}
                     for l in _layer_data for f in l.features_at(latlng)]
    })


OVERLAYS = [
    {'name': 'conservare-scispa', 'title': u"SCI + SPA"},
    {'name': 'conservare-etc',    'title': u"Alte zone protejate"},
    {'name': 'administrativ',     'title': u"Administrativ"},
    {'name': 'ape',               'title': u"Ape"},
    {'name': 'infrastructura',    'title': u"Infrastructură"},
]


_layer_data = []
for spec in OVERLAYS:
    geojson_folder = path(__file__).parent.parent/'geo'/'geojson-layers'
    geojson_path = geojson_folder/('%s.geojson' % spec['name'])
    if geojson_path.isfile():
        _layer_data.append(polygons.Layer(spec['name'], geojson_path))


def default_overlays(app):
    URL_TMPL = app.config.get('TILES_URL_TEMPLATE', '')
    visible = ['conservare-scispa', 'conservare-etc']
    return [dict(spec, **{
            'urlTemplate': URL_TMPL % {'name': spec['name']},
            'visible': bool(spec['name'] in visible),
        }) for spec in OVERLAYS]


def register(app, url_prefix='/map'):
    app.register_blueprint(tinygis, url_prefix=url_prefix)
    app.config.setdefault('AVAILABLE_OVERLAYS', default_overlays(app))
    db = SqliteDict(path(app.instance_path)/'tinygis.db', autocommit=True)
    app.extensions['tinygis-db'] = db
