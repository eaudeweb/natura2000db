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


@tinygis.route('/userlayers', methods=['POST'])
@auth.require_login
def userlayers_create():
    print flask.g.user_id, flask.request.json
    return ""


def register(app, url_prefix='/map'):
    app.register_blueprint(tinygis, url_prefix=url_prefix)
    db = SqliteDict(ppath(app.instance_path)/'tinygis.db', autocommit=True),
    app.extensions['tinygis-db'] = db
