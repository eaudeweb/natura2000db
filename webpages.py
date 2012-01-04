import flask
import blinker
import schema
import widgets
from storage import get_db
import statistics


webpages = flask.Blueprint('webpages', __name__)


@webpages.route('/')
def index():
    form = widgets.MarkupGenerator(flask.current_app.jinja_env)
    return flask.render_template('index.html', form=form,
                                 search_form=schema.Search())


@webpages.route('/view')
def view():
    doc_id = flask.request.args.get('doc_id')
    db = get_db()
    doc = db.load_document(doc_id)
    form = widgets.MarkupGenerator(flask.current_app.jinja_env)
    return flask.render_template('view.html', doc=doc, form=form, doc_id=doc_id)


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
            return flask.redirect('/')

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
    search_answer = db.search(search_form.value)
    form = widgets.SearchMarkupGenerator(flask.current_app.jinja_env)
    form['facets'] = search_answer['facets']
    return flask.render_template('search.html', form=form,
                                 search_form=search_form,
                                 search_answer=search_answer)


@webpages.route('/stats')
def stats():
    args = flask.request.args.to_dict()

    db = get_db()
    search_form = schema.Search.from_flat(args)
    search_answer = db.search(search_form.value, get_data=True)

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
