import os.path
import json
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
