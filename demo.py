#!/usr/bin/env python
# encoding: utf-8

import flask
from flatland.out.markup import Generator
from schema import Species
from storage import Storage


app = flask.Flask(__name__)

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
    rows = [
        Species({'name': u'cioară', 'site': {'isolation': 'B'}}, name='1'),
        Species({'name': u'rață', 'site': {'isolation': 'C'}}, name='2'),
        Species(),
    ]
    return flask.render_template('index.html', schema=Species(), rows=rows)


@app.route('/save', methods=['POST'])
def save():
    import flatland
    from pprint import pformat
    from werkzeug.utils import escape
    SpeciesList = flatland.List.of(Species)
    sl = SpeciesList.from_flat(flask.request.form.to_dict())

    if not sl.validate():
        return flask.render_template('index.html', schema=Species(), rows=sl)

    db = Storage(flask.current_app.config['STORAGE_PATH'])
    for doc_id, species in enumerate(sl):
        db.save_document(doc_id, species.value)

    return "<pre>" + escape(pformat(sl.value)) + "</pre>"


if __name__ == '__main__':
    app.run(debug=True)
