import unittest
import py


class FormsTest(unittest.TestCase):

    def setUp(self):
        self.tmp = py.path.local.mkdtemp()
        self.addCleanup(self.tmp.remove)

    def test_minimal_add(self):
        pass
