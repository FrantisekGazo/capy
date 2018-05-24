import unittest
import tempfile
from capy.conf import Config
from capy.error import CapyException


class ConfTest(unittest.TestCase):
    def setUp(self):
        pass

    def cleanUp(self):
        pass

    def test_fail_parsing_of_missing_file(self):
        try:
            Config(file_name=None)
        except CapyException as e:
            self.assertTrue('Missing configuration file' in e.message)

    def test_fail_parsing_of_empty(self):
        with tempfile.NamedTemporaryFile() as temp:
            try:
                Config(file_name=temp.name)
            except CapyException as e:
                self.assertTrue('BDS configuration is missing' in e.message)

    def test_parsing_of_minimum_content(self):
        with tempfile.NamedTemporaryFile() as temp:
            self.__write(temp, [
                'bds:',
                '  customer: TestCustomer',
                '  project: TestProject'
            ])

            config = Config(file_name=temp.name)

            self.assertIsNotNone(config)

    def __write(self, tmp_file, lines):
        with open(tmp_file.name, 'w') as file:
            content = '\n'.join(lines)
            file.write(content)


if __name__ == '__main__':
    unittest.main()
