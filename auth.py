from functools import wraps
from path import path as ppath
import flask
from flaskext.openid import OpenID, COMMON_PROVIDERS
from sqlitedict import SqliteDict

oid = OpenID()

auth = flask.Blueprint('auth', __name__)


def _get_users_db():
    return flask.current_app.extensions['auth-users']['usersdb']


def lookup_current_user():
    flask.g.user = None
    flask.g.user_id = flask.session.get('openid_url')
    if flask.g.user_id is not None:
        users_db = _get_users_db()
        flask.g.user = users_db.get(flask.g.user_id)


@auth.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if flask.g.user is not None:
        return flask.redirect(oid.get_next_url())

    return oid.try_login(COMMON_PROVIDERS['google'],
                         ask_for=['email', 'fullname', 'nickname'])


@oid.after_login
def update_user(resp):
    users_db = _get_users_db()
    flask.g.user_id = flask.session['openid_url'] = resp.identity_url
    flask.g.user = users_db.get(flask.g.user_id) or {}
    flask.g.user.update({
        'name': resp.fullname or resp.nickname or u"",
        'email': resp.email,
    })
    save_user()
    return flask.redirect(oid.get_next_url())


def save_user():
    assert flask.g.user_id
    assert flask.g.user
    users_db = _get_users_db()
    users_db[flask.g.user_id] = flask.g.user


def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if flask.g.user is None:
            flask.abort(403)

        return func(*args, **kwargs)

    return wrapper


@auth.route('/logout')
def logout():
    flask.session.pop('openid_url', None)
    return flask.redirect(oid.get_next_url())


def register(app):
    app.register_blueprint(auth)
    oid.init_app(app)
    instance_path = ppath(app.instance_path)
    oid.fs_store_path = instance_path/'openid-store'
    app.before_request(lookup_current_user)
    app.extensions['auth-users'] = {
        'usersdb': SqliteDict(instance_path/'users.db', autocommit=True),
    }
