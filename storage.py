import os.path
import json
import re
import logging
import urllib
import urllib2
import errno
from contextlib import contextmanager
import flask
from bson.objectid import ObjectId
import schema

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class StorageError(Exception):
    pass


QUERY_ROWS = 1000


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


class MongoStorage(object):

    def __init__(self, db_name):
        self.connection = pymongo.Connection('localhost', 27017)
        self.db = self.connection[db_name]

    def save_document(self, doc_id, doc):
        data = doc.value
        if doc_id is not None:
            data = dict(data, _id=ObjectId(doc_id))
            log.info("saving new document %r")
        else:
            log.info("saving document %r", doc_id)

        doc_id = self.db['spadoc'].insert(data)
        return doc_id

    def load_document(self, doc_id):
        doc = self.db['spadoc'].find_one({'_id': ObjectId(doc_id)})
        if doc is None:
            return schema.SpaDoc()
        del doc['_id']
        return schema.SpaDoc(doc)

    def document_ids(self):
        doc_id_list = [doc['_id'] for doc in self.db['spadoc'].find()]
        doc_id_list.sort()
        return doc_id_list


try:
    import pymongo
except ImportError:
    MongoStorage = None


class SolrStorage(object):

    orig_field_name = 'orig'
    solr_base_url = 'http://localhost:8983/solr/'

    def _solr_doc(self, doc):
        data = doc.value

        solr_doc = {
            'id': data['section1']['sitecode'],
            self.orig_field_name: json.dumps(data),
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
            if e.reason.errno == errno.ECONNREFUSED:
                raise StorageError("Could not connect to Solr", e)
            else:
                raise

        try:
            yield response
        finally:
            response.close()

    def solr_query(self, query):
        url = self.solr_base_url + 'select?q=%s&wt=json&rows=%d' % (
                query, QUERY_ROWS)
        with self.solr_http(url) as http_response:
            answer = json.load(http_response)

        num_found = answer['response']['numFound']
        if num_found > QUERY_ROWS:
            log.warn("Found more results than expected: %d > %d",
                     num_found, QUERY_ROWS)

        return answer['response']['docs']

    def save_document(self, doc_id, doc):
        return self.save_document_batch([doc])[0]

    def save_document_batch(self, batch):
        url = self.solr_base_url + 'update/json?commit=true'
        request = urllib2.Request(url)
        request.add_header('Content-Type', 'application/json')
        request.add_data(json.dumps([self._solr_doc(doc) for doc in batch]))

        with self.solr_http(request) as response:
            response.read()

        return [doc['section1']['sitecode'].value for doc in batch]

    def load_document(self, doc_id):
        doc = self.solr_query('id:%s' % doc_id)[0]
        return schema.SpaDoc(json.loads(doc[self.orig_field_name]))

    def document_ids(self):
        return sorted([d['id'] for d in self.solr_query('*')])


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
