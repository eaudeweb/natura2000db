#!/usr/bin/env python

import sys
import os
import logging
import flask
import flaskext.script
import schema
import webpages
from storage import get_db


default_config = {
    'DEBUG': False,
    'ERROR_LOG_FILE': None,
    'HTTP_LISTEN_HOST': '127.0.0.1',
    'HTTP_PROXIED': False,
    'HTTP_CHERRYPY': False,
}


def create_app():
    app = flask.Flask(__name__)

    app.config.update(default_config)
    app.config.from_pyfile('default_config.py')
    if 'APP_SETTINGS' in os.environ:
        app.config.from_envvar('APP_SETTINGS')

    webpages.register(app)

    if 'PDF_FOLDER' in app.config:
        from werkzeug.wsgi import SharedDataMiddleware
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static/pdf': app.config['PDF_FOLDER'],
        })

    return app


manager = flaskext.script.Manager(create_app)


@manager.command
def accessdb_mjson(indent=False):
    logging.getLogger('migrations.from_access').setLevel(logging.INFO)

    from migrations.from_access import load_from_sql, verify_data
    kwargs = {'indent': 2} if indent else {}
    for doc in verify_data(load_from_sql()):
        flask.json.dump(doc, sys.stdout, **kwargs)
        sys.stdout.write('\n')


@manager.command
def import_mjson():
    logging.getLogger('storage').setLevel(logging.INFO)

    def batched(iterator, count=10):
        batch = []
        for value in iterator:
            batch.append(value)
            if len(batch) >= count:
                yield batch
                batch = []
        if batch:
            yield batch

    def read_json_lines(stream):
        for line in stream:
            yield flask.json.loads(line)

    def load_document(data):
        doc = schema.SpaDoc(data)
        assert doc.validate(), '%s does not validate' % data['section1']['code']
        assert doc.value == data, 'failed round-tripping the json data'
        return doc

    db = get_db(create_app())

    for batch in batched(load_document(d) for d in read_json_lines(sys.stdin)):
        db.save_document_batch(batch)
        sys.stdout.write('.')
        sys.stdout.flush()

    print ' done'


@manager.command
def runserver(verbose=False):
    app = create_app()

    if verbose:
        storage_logger = logging.getLogger('storage')
        storage_logger.setLevel(logging.DEBUG)
        storage_handler = logging.StreamHandler()
        storage_handler.setLevel(logging.DEBUG)
        storage_logger.addHandler(storage_handler)

    if app.config['ERROR_LOG_FILE'] is not None:
        logging.basicConfig(filename=app.config['ERROR_LOG_FILE'],
                            loglevel=logging.ERROR)

    if app.config['HTTP_PROXIED']:
        from revproxy import ReverseProxied
        app.wsgi_app = ReverseProxied(app.wsgi_app)

    if app.config['HTTP_CHERRYPY']:
        from cherrypy import wsgiserver
        listen = (app.config['HTTP_LISTEN_HOST'], 5000)
        server = wsgiserver.CherryPyWSGIServer(listen, app.wsgi_app)
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()

    else:
        app.run(app.config['HTTP_LISTEN_HOST'])


if __name__ == '__main__':
    manager.run()
