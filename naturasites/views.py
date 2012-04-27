# encoding: utf-8
import os.path
import flask
import blinker
import schema
import widgets
import statistics

from storage import get_db, Or, And, AllowWildcards, StorageError, NotFound
from loader import ZopeTemplateLoader


naturasites = flask.Blueprint('naturasites', __name__,
                              template_folder='templates')


@naturasites.route('/')
def index():
    form = widgets.MarkupGenerator(flask.current_app.jinja_env)
    return flask.render_template('index.html', **{
        'form': form,
        'search_form': schema.Search(),
        'reference_data': schema.reference_data,
    })


def _other_site_labels(doc):
    db = get_db()
    other_site_ids = Or(o.value for o in doc['section1']['other_sites'])
    results = db.search({'id': other_site_ids})
    return dict((data['id'], data['name']) for data in results['docs'])


@naturasites.route('/view')
def view():
    doc_id = flask.request.args.get('doc_id')
    db = get_db()
    try:
        doc = db.load_document(doc_id)
    except NotFound:
        flask.abort(404)
    form = widgets.MarkupGenerator(flask.current_app.jinja_env)
    form.other_site_labels = _other_site_labels(doc)
    options = {
        'title': _doc_title(doc),
        'form': form,
        'doc_id': doc_id,
        'doc': doc,
    }

    app = flask.current_app
    if 'PDF_URL' in app.config:
        pdf_name = doc_id.lower() + '.pdf'
        options['pdf_url'] = app.config['PDF_URL'] + pdf_name
    return flask.render_template('view.html', **options)


def _doc_title(doc):
    return u"%s (%s)" % (doc['section1']['name'].u, doc['section1']['code'].u)


class SearchError(Exception):
    """ Error occurred during search """


def _db_search(search_form, **kwargs):
    db = get_db()
    query = search_form.value

    text_str = (query.pop('text') or u"").strip()
    if any(text_str.startswith(ch) for ch in ['*', '?']):
        # the Solr QueryParser does not accept leading-wildcard queries
        raise SearchError(u"Textul nu poate să înceapă cu '*' sau '?'")

    text = AllowWildcards(text_str)
    text_or = Or([('name', text), ('text', text)])
    full_query = And([text_or, query])

    try:
        return db.search(full_query, **kwargs)
    except StorageError, e:
        raise SearchError(u"Eroare bază de date: %s" % e)


@naturasites.route('/search')
def search():
    form = widgets.SearchMarkupGenerator(flask.current_app.jinja_env)
    search_form = schema.Search.from_flat(flask.request.args.to_dict())

    try:
        search_answer = _db_search(search_form, facets=True)
    except SearchError, e:
        return flask.render_template('search_error.html', msg=unicode(e),
                                     form=form, search_form=search_form)

    if "nuts2" in search_form and search_form["nuts2"]:
        search_answer['facets']['nuts3'] = [
            e for e in search_answer['facets']['nuts3']
              if e.name.startswith(search_form['nuts2'].value)]
    form['facets'] = search_answer['facets']

    return flask.render_template('search.html', form=form,
                                 search_form=search_form,
                                 search_answer=search_answer,
                                 stat_labels=statistics.label)


@naturasites.route('/stats')
def stats():
    args = flask.request.args.to_dict()

    search_form = schema.Search.from_flat(args)
    stat_form = schema.Statistics.from_flat(args)
    get_data = statistics.need_data(stat_form)

    try:
        search_answer = _db_search(search_form, get_data=get_data, facets=True)
    except SearchError, e:
        return flask.render_template('error.html', msg=unicode(e))

    stat_html = statistics.compute(stat_form, search_answer)

    form = widgets.SearchMarkupGenerator(flask.current_app.jinja_env)
    form['view_name'] = 'naturasites.stats'
    form['facets'] = search_answer['facets']
    return flask.render_template('stats.html', form=form,
                                 stat_form=stat_form,
                                 stat_labels=statistics.label,
                                 stat_html=stat_html)

@naturasites.route('/data/<string:name>')
def reference_data(name):
    try:
        dataset = schema.reference_data[name]
    except KeyError:
        flask.abort(404)

    fmt = flask.request.args.get('fmt', 'html')
    if fmt == 'json':
        return flask.jsonify(dataset['mapping'])

    return flask.render_template('datasets.html', **{
        'dataset_name': name,
        'dataset': dataset,
    })

@naturasites.route('/dump')
def dump():
    db = get_db()
    docs = db.search({}, get_data=True)['docs']
    return flask.jsonify(dict((d['id'], d['data']) for d in docs))


def register(app):
    app.register_blueprint(naturasites)
    app.document_signal = blinker.Signal()
