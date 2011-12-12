import os.path
import json
import re
import logging

log = logging.getLogger(__name__)


class Storage(object):

    def __init__(self, storage_path):
        self.storage_path = storage_path

    def _doc_path(self, doc_id):
        return os.path.join(self.storage_path, 'doc_%d.json' % doc_id)

    def save_document(self, doc_id, data):
        assert isinstance(doc_id, int)
        log.info("saving document %r", doc_id)
        with open(self._doc_path(doc_id), 'wb') as f:
            json.dump(data, f, indent=2)

    def load_document(self, doc_id):
        assert isinstance(doc_id, int)
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
