import flask


tinygis = flask.Blueprint('tinygis', __name__,
                          template_folder='templates',
                          static_folder='static')


@tinygis.route('/')
def index():
    return flask.render_template('map.html')


def register(app, url_prefix='/map'):
    app.register_blueprint(tinygis, url_prefix=url_prefix)
