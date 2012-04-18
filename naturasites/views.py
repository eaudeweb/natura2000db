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
    return flask.render_template('index.html', form=form,
                                 search_form=schema.Search())


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


@naturasites.route('/new', methods=['GET', 'POST'])
@naturasites.route('/edit', methods=['GET', 'POST'])
def edit():
    doc_id = flask.request.args.get('doc_id', None)
    db = get_db()
    new_doc = bool(doc_id is None)

    if flask.request.method == 'POST':
        request_form = flask.request.form.to_dict()
        request_form["section1_code"] = doc_id
        doc = schema.SpaDoc.from_flat(request_form)

        if doc.validate():
            doc_id = db.save_document(doc_id, doc)
            app = flask.current_app
            app.document_signal.send('save', doc_id=doc_id, doc=doc)
            flask.flash("Document %r saved" % doc_id)
            return flask.redirect(flask.url_for('naturasites.view', doc_id=doc_id))

        else:
            flask.flash("Errors in document")

    else:
        if new_doc:
            doc = schema.SpaDoc()
        else:
            doc = db.load_document(doc_id)

    title = u"Introducere sit nou" if new_doc else _doc_title(doc)
    form = widgets.MarkupGenerator(flask.current_app.jinja_env)
    return flask.render_template('edit.html', title=title,
                                 doc=doc, form=form)


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
def corine_areas(name):
    datasets = {
        'corine': schema.corine_map,
        'text': schema.antropic_activities_map,
        'habitat': schema.habitat_type_map,
        'nuts2': schema.nuts2,
        'nuts3': schema.nuts3,
        'protected_areas': schema.classification_map
    }
    format = flask.request.args.get('fmt', 'html')
    try:
        dataset = datasets[name]
    except KeyError:
        flask.abort(404)

    if format == 'json':
        return flask.jsonify(dataset)
    return flask.render_template('datasets.html',
                                dataset=dataset.items(),
                                dataset_name=name)

@naturasites.route('/dump')
def dump():
    db = get_db()
    docs = db.search({}, get_data=True)['docs']
    return flask.jsonify(dict((d['id'], d['data']) for d in docs))


def register(app):
    app.register_blueprint(naturasites)
    app.document_signal = blinker.Signal()
