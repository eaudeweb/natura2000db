#!/usr/bin/env python
# encoding: utf-8

import flask
from flatland.out.markup import Generator
from schema import Species
from storage import Storage


app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'demo'

import os.path
app.config['STORAGE_PATH'] = os.path.join(os.path.dirname(__file__),
                                          'data', 'documents')

_my_extensions = app.jinja_options['extensions'] + ['jinja2.ext.do']
app.jinja_options = dict(app.jinja_options, extensions=_my_extensions)
app.jinja_env.globals['form_generator'] = Generator('html')


from flatland.signals import validator_validated
from flatland.schema.base import NotEmpty
@validator_validated.connect
def validated(sender, element, result, **kwargs):
    if sender is NotEmpty:
        if not result:
            element.add_error("required")


@app.route('/')
def index():
    db = Storage(flask.current_app.config['STORAGE_PATH'])
    return flask.render_template('index.html', doc_id_list=db.document_ids())


@app.route('/edit/<int:doc_id>', methods=['GET', 'POST'])
def edit(doc_id):
    db = Storage(flask.current_app.config['STORAGE_PATH'])

    if flask.request.method == 'POST':
        species = Species.from_flat(flask.request.form.to_dict())

        if species.validate():
            db.save_document(doc_id, species.value)
            flask.flash("Document %d saved" % doc_id)
            return flask.redirect('/')

    else:
        species = Species(db.load_document(doc_id))

    return flask.render_template('edit.html', doc=species)


if __name__ == '__main__':
    app.run(debug=True)
