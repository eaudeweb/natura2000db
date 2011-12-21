import unittest
import py


def _create_test_app(tmp):
    from demo import create_app
    app = create_app()
    app.config['STORAGE_ENGINE'] = 'filesystem'
    app.config['STORAGE_FS_PATH'] = str((tmp/'storage').ensure(dir=True))
    return app


class FormsTest(unittest.TestCase):

    def setUp(self):
        self.tmp = py.path.local.mkdtemp()
        self.addCleanup(self.tmp.remove)
        self.app = _create_test_app(self.tmp)

    def test_minimal_add(self):
        self.doc = None
        def doc_saved(name, doc_id, doc):
            self.doc_id = doc_id
            self.doc = doc

        self.app.document_signal.connect(doc_saved, sender='save')

        client = self.app.test_client()
        form_data = {
            'section1_type': 'K',
            'section1_sitecode': 'asdfqwer3',
            'section1_date': '200503',
            'section1_site_name': 'Firul Ierbii',
            'section2_regcod_0_reg_code': '',
            'section2_regcod_0_reg_name': 'Poiana',
            'section2_regcod_0_cover': '',
            'section2_bio_region_alpine': '1',
        }
        response = client.post('/new', data=form_data, follow_redirects=True)
        self.assertIsNotNone(self.doc)
        self.assertIn("Document %r saved" % self.doc_id, response.data)
