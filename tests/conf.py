import unittest


class ConfTest(unittest.TestCase):
    def setUp(self):
        pass

    def cleanUp(self):
        pass

    def test_parsing(self):
        self.assertEquals(4, 4)

if __name__ == '__main__':
    unittest.main()
