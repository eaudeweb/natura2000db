import flask
import polygons


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


def register(app, url_prefix='/map'):
    app.register_blueprint(tinygis, url_prefix=url_prefix)
