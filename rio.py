#!/usr/bin/env python

import sys
import os
import logging
import flask
import schema
import webpages
from storage import get_db


def create_app():
    app = flask.Flask(__name__)

    webpages.register(app)

    app.config.from_pyfile('default_config.py')
    if 'APP_SETTINGS' in os.environ:
        app.config.from_envvar('APP_SETTINGS')

    if 'PDF_FOLDER' in app.config:
        from werkzeug.wsgi import SharedDataMiddleware
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static/pdf': app.config['PDF_FOLDER'],
        })

    return app


def accessdb_mjson(args):
    logging.getLogger('migrations.from_access').setLevel(logging.INFO)

    from migrations.from_access import load_from_sql, verify_data
    kwargs = {'indent': 2} if args.indent else {}
    for doc in verify_data(load_from_sql()):
        flask.json.dump(doc, sys.stdout, **kwargs)
        sys.stdout.write('\n')


def import_mjson(args):
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


def runserver(args):
    app = create_app()

    if 'ERROR_LOG_FILE' in app.config:
        logging.basicConfig(filename=app.config['ERROR_LOG_FILE'],
                            loglevel=logging.ERROR)

    if args.verbose:
        logging.getLogger('werkzeug').setLevel(logging.INFO)
        logging.getLogger('storage').setLevel(logging.DEBUG)
        logging.basicConfig(loglevel=logging.DEBUG)
    else:
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

    host = '0.0.0.0' if args.listen_all else '127.0.0.1'

    if args.proxied:
        from revproxy import ReverseProxied
        app.wsgi_app = ReverseProxied(app.wsgi_app)

    if args.cherrypy:
        from cherrypy import wsgiserver
        server = wsgiserver.CherryPyWSGIServer((host, 5000), app)
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()

    else:
        app.run(host)


def shell(args):
    from code import interact
    app = create_app()
    interact(local={'app': app})


def create_argument_parser():
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_runserver = subparsers.add_parser('runserver')
    parser_runserver.set_defaults(func=runserver)
    parser_runserver.add_argument('--cherrypy', action='store_true')
    parser_runserver.add_argument('--proxied', action='store_true')
    parser_runserver.add_argument('--listen-all', action='store_true')
    parser_runserver.add_argument('-v', '--verbose', action='store_true')

    parser_accessdb_mjson = subparsers.add_parser('accessdb_mjson')
    parser_accessdb_mjson.set_defaults(func=accessdb_mjson)
    parser_accessdb_mjson.add_argument('-i', '--indent', action='store_true')

    parser_import_mjson = subparsers.add_parser('import_mjson')
    parser_import_mjson.set_defaults(func=import_mjson)

    parser_import_mjson = subparsers.add_parser('shell')
    parser_import_mjson.set_defaults(func=shell)

    return parser


if __name__ == '__main__':
    args = create_argument_parser().parse_args()
    args.func(args)
