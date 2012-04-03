import flask


tinygis = flask.Blueprint('tinygis', __name__,
                          template_folder='templates')


@tinygis.route('/')
def index():
    return "hi tinygis"


def register(app, url_prefix='/map'):
    app.register_blueprint(tinygis, url_prefix=url_prefix)
