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
        pass
