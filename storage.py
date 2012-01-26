import os.path
import json
import re
import logging
import urllib
import urllib2
import errno
from contextlib import contextmanager
from collections import namedtuple
import flask
import schema

log = logging.getLogger(__name__)


class StorageError(Exception):
    pass


class NotFound(StorageError):
    pass


QUERY_ROWS = 1000


SolrAnswer = namedtuple('SolrAnswer', ['docs', 'facets'])
FacetItem = namedtuple('FacetItem', ['name', 'count'])


class Or(list):
    """ Marker class used to ask for the 'or' query operation """

And = list # the 'and' query operation is default

class AllowWildcards(unicode):
    """ don't quote the wildcard character """


class FsStorage(object):

    def __init__(self, storage_path):
        self.storage_path = storage_path

    def _doc_path(self, doc_id):
        doc_id = int(doc_id)
        return os.path.join(self.storage_path, 'doc_%d.json' % doc_id)

    def save_document(self, doc_id, doc):
        data = doc.value
        if doc_id is None:
            doc_id = max([-1] + self.document_ids()) + 1
        else:
            doc_id = int(doc_id)
        log.info("saving document %r", doc_id)
        with open(self._doc_path(doc_id), 'wb') as f:
            json.dump(data, f, indent=2)
        return doc_id

    def load_document(self, doc_id):
        doc_id = int(doc_id)
        with open(self._doc_path(doc_id), 'rb') as f:
            return schema.SpaDoc(json.load(f))

    def document_ids(self):
        doc_id_list = []
        for name in os.listdir(self.storage_path):
            m = re.match(r'^doc_(?P<doc_id>\d+)\.json$', name)
            if m is None:
                continue

            doc_id_list.append(int(m.group('doc_id')))

        doc_id_list.sort()
        return doc_id_list


_solr_text_pattern = re.compile(r'([\\+\-&|!(){}[\]^~*?:"; ])')
_solr_text_wildcards_ok_pattern = re.compile(r'([\\+\-&|!(){}[\]^~?:"; ])')
def quote_solr_text(text, wildcards_ok=False):
    if wildcards_ok:
        pattern = _solr_text_wildcards_ok_pattern
    else:
        pattern = _solr_text_pattern
    return pattern.sub(r'\\\1', text);


def quote_solr_query(value, op=u' AND '):
    if isinstance(value, str):
        value = unicode(value)

    if isinstance(value, AllowWildcards):
        return quote_solr_text(value, wildcards_ok=True)
    elif isinstance(value, unicode):
        return quote_solr_text(value) if value else u''
    elif isinstance(value, Or):
        return quote_solr_query(list(value), op=u' OR ')
    elif isinstance(value, And):
        quoted = filter(None, map(quote_solr_query, value))
        return u'(%s)' % (op.join(quoted),) if quoted else u''
    elif isinstance(value, dict):
        quoted = filter(None, map(quote_solr_query, value.iteritems()))
        return u'(%s)' % (op.join(quoted),) if quoted else u''
    elif isinstance(value, tuple) and len(value) == 2:
        k, v = value
        if not v:
            return u''
        return u'(%s:%s)' % (quote_solr_query(k), quote_solr_query(v))
    else:
        raise ValueError("Can't quote value of type %r" % type(value))


class SolrStorage(object):

    solr_base_url = 'http://localhost:8983/solr/'

    def _solr_doc(self, doc):
        data = doc.value

        solr_doc = {
            'id': data['section1']['code'],
            'name': data['section1']['name'],
            'orig': json.dumps(data),
        }

        for element in schema.Search().all_children:
            value = element.properties['index'](doc)
            log.debug('index %s: %r', element.name, value)
            solr_doc[element.name] = value

        return solr_doc

    @contextmanager
    def solr_http(self, request):
        if isinstance(request, urllib2.Request):
            url = request.get_full_url()
        else:
            url = request

        log.debug("Solr request to url %r", url)

        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError, e:
            if hasattr(e, 'reason') and e.reason.errno == errno.ECONNREFUSED:
                raise StorageError("Nu se poate stabili conexiunea")
            else:
                raise

        try:
            yield response
        finally:
            response.close()

    def solr_query(self, query, args=[]):
        full_args = [('q', query.encode('utf-8'))] + args + [
            ('wt', 'json'),
            ('rows', str(QUERY_ROWS)),
        ]
        url = self.solr_base_url + 'select?' + urllib.urlencode(full_args)

        with self.solr_http(url) as http_response:
            answer = json.load(http_response)

        num_found = answer['response']['numFound']
        if num_found > QUERY_ROWS:
            log.warn("Found more results than expected: %d > %d",
                     num_found, QUERY_ROWS)

        def pairs(values):
            values = iter(values)
            while True:
                yield values.next(), values.next()

        facets = {}
        if 'facet_counts' in answer:
            for name, values in answer['facet_counts']['facet_fields'].iteritems():
                facets[name] = [FacetItem(*p) for p in pairs(values) if p[1] > 0]

        return SolrAnswer(answer['response']['docs'], facets)

    def save_document(self, doc_id, doc):
        return self.save_document_batch([doc])[0]

    def save_document_batch(self, batch):
        url = self.solr_base_url + 'update/json?commit=true'
        request = urllib2.Request(url)
        request.add_header('Content-Type', 'application/json')
        request.add_data(json.dumps([self._solr_doc(doc) for doc in batch]))

        with self.solr_http(request) as response:
            response.read()

        return [doc['section1']['code'].value for doc in batch]

    def load_document(self, doc_id):
        docs = self.solr_query('id:%s' % doc_id).docs
        if not docs:
            raise NotFound()
        doc = docs[0]
        return schema.SpaDoc(json.loads(doc['orig']))

    def document_ids(self):
        return sorted([d['id'] for d in self.solr_query('*').docs])

    def search(self, criteria, get_data=False, facets=False):
        query = quote_solr_query(criteria)
        if not query:
            query = '*:*'

        log.debug('Solr query %r', query)

        args = []

        if facets:
            args.append( ('facet', 'true') )

            for element in schema.Search().all_children:
                if element.properties.get('facet', False):
                    args.append( ('facet.field', element.name) )

        want_fields = ['id', 'name']
        if get_data:
            want_fields.append('orig')
        args.append( ('fl', ','.join(want_fields)) )

        answer = self.solr_query(query, args)
        docs = [{
                'id': r['id'],
                'name': r['name'],
                'data': json.loads(r.get('orig', '{}')),
            } for r in answer.docs]

        return {
            'docs': docs,
            'facets': answer.facets,
        }


def get_db(app=None):
    if app is None:
        app = flask.current_app
    config = app.config
    engine_name = config['STORAGE_ENGINE']

    if engine_name == 'solr':
        return SolrStorage()

    elif engine_name == 'filesystem':
        return FsStorage(config['STORAGE_FS_PATH'])

    else:
        raise ValueError('Unknown storage engine %r' % engine_name)
