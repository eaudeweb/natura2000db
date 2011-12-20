import os.path
import json
import re
import logging
import urllib2
import flask
from bson.objectid import ObjectId

log = logging.getLogger(__name__)


class FsStorage(object):

    def __init__(self, storage_path):
        self.storage_path = storage_path

    def _doc_path(self, doc_id):
        doc_id = int(doc_id)
        return os.path.join(self.storage_path, 'doc_%d.json' % doc_id)

    def save_document(self, doc_id, data):
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
            return json.load(f)

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

    def save_document(self, doc_id, data):
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
            return {}
        del doc['_id']
        return doc

    def document_ids(self):
        doc_id_list = [doc['_id'] for doc in self.db['spadoc'].find()]
        doc_id_list.sort()
        return doc_id_list


try:
    import pymongo
except ImportError:
    MongoStorage = None


class SolrStorage(object):

    orig_field_name = 'orig_s'
    solr_base_url = 'http://localhost:8983/solr/'

    def _solr_doc(data):
        full_text = (
            data['section1']['site_name'] +
            data['section4']['quality'] +
            data['section4']['vulnar'] +
            data['section4']['docum'])

        return {
            'id': data['section1']['sitecode'],
            'title': data['section1']['site_name'],
            'type_txt': data['section1']['type'],
            'text': full_text,
            self.orig_field_name: json.dumps(data),
        }

    def save_document(self, doc_id, data):

        url = self.solr_base_url + 'update/json?commit=true'
        request = urllib2.Request(url)
        request.add_header('Content-Type', 'application/json')
        request.add_data(json.dumps([self._solr_doc(data)]))

        response = urllib2.urlopen(request)
        response.read()
        response.close()

        return data['section1']['sitecode']

    def load_document(self, doc_id):
        url = self.solr_base_url + 'select?q=id:%s&wt=json' % doc_id
        response = urllib2.urlopen(url)
        results = json.load(response)
        response.close()
        return json.loads(results['response']['docs'][0][self.orig_field_name])

    def document_ids(self):
        url = self.solr_base_url + 'select?q=*&wt=json'
        response = urllib2.urlopen(url)
        results = json.load(response)
        response.close()
        return sorted([d['id'] for d in results['response']['docs']])


def get_db():
    config = flask.current_app.config
    engine_name = config['STORAGE_ENGINE']

    if engine_name == 'solr':
        return SolrStorage()

    elif engine_name == 'filesystem':
        return FsStorage(config['STORAGE_FS_PATH'])

    else:
        raise ValueError('Unknown storage engine %r' % engine_name)
