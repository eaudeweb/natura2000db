# encoding: utf-8
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
    openid_url = flask.session.get('openid_url')
    if openid_url is not None:
        users_db = _get_users_db()
        flask.g.user = users_db.get(openid_url)


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
    openid_url = flask.session['openid_url'] = resp.identity_url
    flask.g.user = users_db.get(openid_url) or {}
    flask.g.user.update({
        'name': resp.fullname or resp.nickname or u"",
        'email': resp.email,
    })
    save_user()
    return flask.redirect(oid.get_next_url())


def save_user():
    assert flask.session['openid_url']
    assert flask.g.user
    users_db[flask.session['openid_url']] = flask.g.user


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
