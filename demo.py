#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import logging
import flask
import blinker
import schema
from storage import get_db
from widgets import install_widgets


webpages = flask.Blueprint('webpages', __name__)


@webpages.route('/')
def index():
    db = get_db()
    return flask.render_template('index.html', doc_id_list=db.document_ids())


@webpages.route('/view')
def view():
    doc_id = flask.request.args.get('doc_id')
    db = get_db()
    doc = schema.SpaDoc(db.load_document(doc_id))
    return flask.render_template('view.html', doc=doc)


@webpages.route('/new', methods=['GET', 'POST'])
@webpages.route('/edit', methods=['GET', 'POST'])
def edit():
    doc_id = flask.request.args.get('doc_id', None)
    db = get_db()

    if flask.request.method == 'POST':
        doc = schema.SpaDoc.from_flat(flask.request.form.to_dict())

        if doc.validate():
            doc_id = db.save_document(doc_id, doc.value)
            app = flask.current_app
            app.document_signal.send('save', doc_id=doc_id, doc=doc)
            flask.flash("Document %r saved" % doc_id)
            return flask.redirect('/')

        else:
            flask.flash("Errors in document")

    else:
        if doc_id is None:
            doc = schema.SpaDoc()
        else:
            doc = schema.SpaDoc(db.load_document(doc_id))

    return flask.render_template('edit.html', doc=doc)


@webpages.route('/search')
def search():
    search_form = schema.Search(flask.request.args.to_dict())
    return flask.render_template('search.html', search_form=search_form)


def create_app():
    app = flask.Flask(__name__)
    app.document_signal = blinker.Signal()

    app.register_blueprint(webpages)

    _my_extensions = app.jinja_options['extensions'] + ['jinja2.ext.do']
    app.jinja_options = dict(app.jinja_options, extensions=_my_extensions)
    install_widgets(app.jinja_env)

    app.config.from_pyfile('default_config.py')
    if 'APP_SETTINGS' in os.environ:
        app.config.from_envvar('APP_SETTINGS')

    return app


def accessdb_mjson(args):
    from migrations.from_access import load_from_sql, verify_data
    kwargs = {'indent': 2} if args.indent else {}
    for doc in verify_data(load_from_sql()):
        flask.json.dump(doc, sys.stdout, **kwargs)
        sys.stdout.write('\n')


def import_mjson(args):

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

    db = get_db(create_app())

    for batch in batched(read_json_lines(sys.stdin)):
        db.save_document_batch(batch)
        sys.stdout.write('.')
        sys.stdout.flush()

    print ' done'


def runserver(args):
    from revproxy import ReverseProxied
    app = create_app()
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    app.run(debug=True)


def create_argument_parser():
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_runserver = subparsers.add_parser('runserver')
    parser_runserver.set_defaults(func=runserver)

    parser_accessdb_mjson = subparsers.add_parser('accessdb_mjson')
    parser_accessdb_mjson.set_defaults(func=accessdb_mjson)
    parser_accessdb_mjson.add_argument('-i', '--indent', action='store_true')

    parser_import_mjson = subparsers.add_parser('import_mjson')
    parser_import_mjson.set_defaults(func=import_mjson)

    return parser


if __name__ == '__main__':
    logging.basicConfig(loglevel=logging.DEBUG)
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    args = create_argument_parser().parse_args()
    args.func(args)
