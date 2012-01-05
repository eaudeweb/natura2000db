import flask
import blinker
import schema
import widgets
from storage import get_db, OrList
import statistics


webpages = flask.Blueprint('webpages', __name__)


@webpages.route('/')
def index():
    form = widgets.MarkupGenerator(flask.current_app.jinja_env)
    return flask.render_template('index.html', form=form,
                                 search_form=schema.Search())


def _other_site_labels(doc):
    db = get_db()
    other_site_ids = OrList(o.value for o in doc['section1']['other_sites'])
    results = db.search({'id': other_site_ids})
    return dict((data['id'], data['name']) for data in results['docs'])


@webpages.route('/view')
def view():
    doc_id = flask.request.args.get('doc_id')
    db = get_db()
    doc = db.load_document(doc_id)
    form = widgets.MarkupGenerator(flask.current_app.jinja_env)
    form.other_site_labels = _other_site_labels(doc)
    return flask.render_template('view.html', form=form, doc=doc, doc_id=doc_id)


@webpages.route('/new', methods=['GET', 'POST'])
@webpages.route('/edit', methods=['GET', 'POST'])
def edit():
    doc_id = flask.request.args.get('doc_id', None)
    db = get_db()

    if flask.request.method == 'POST':
        doc = schema.SpaDoc.from_flat(flask.request.form.to_dict())

        if doc.validate():
            doc_id = db.save_document(doc_id, doc)
            app = flask.current_app
            app.document_signal.send('save', doc_id=doc_id, doc=doc)
            flask.flash("Document %r saved" % doc_id)
            return flask.redirect(flask.url_for('webpages.view', doc_id=doc_id))

        else:
            flask.flash("Errors in document")

    else:
        if doc_id is None:
            doc = schema.SpaDoc()
        else:
            doc = db.load_document(doc_id)

    form = widgets.MarkupGenerator(flask.current_app.jinja_env)
    return flask.render_template('edit.html', doc=doc, form=form)


@webpages.route('/search')
def search():
    db = get_db()
    search_form = schema.Search.from_flat(flask.request.args.to_dict())
    search_answer = db.search(search_form.value, facets=True)
    form = widgets.SearchMarkupGenerator(flask.current_app.jinja_env)
    form['facets'] = search_answer['facets']
    return flask.render_template('search.html', form=form,
                                 search_form=search_form,
                                 search_answer=search_answer,
                                 available_stats=statistics.compute.keys())


@webpages.route('/stats')
def stats():
    args = flask.request.args.to_dict()

    db = get_db()
    search_form = schema.Search.from_flat(args)
    search_answer = db.search(search_form.value, get_data=True, facets=True)

    stat_form = schema.Statistics.from_flat(args)
    stat_name = stat_form['compute'].value
    stat_html = statistics.compute[stat_name](stat_form, search_answer)

    form = widgets.SearchMarkupGenerator(flask.current_app.jinja_env)
    form['view_name'] = 'webpages.stats'
    form['facets'] = search_answer['facets']
    return flask.render_template('stats.html', form=form,
                                 stat_form=stat_form,
                                 stat_html=stat_html)


def register(app):
    app.register_blueprint(webpages)
    app.document_signal = blinker.Signal()

    _my_extensions = app.jinja_options['extensions'] + ['jinja2.ext.do']
    app.jinja_options = dict(app.jinja_options, extensions=_my_extensions)
