import unittest
import os
import tempfile
from runners.run_compare_yml import main

class TestRunCompareYML(unittest.TestCase):
    def setUp(self):
        self.input_file1 = tempfile.NamedTemporaryFile(delete=False, suffix='.yml')
        self.input_file2 = tempfile.NamedTemporaryFile(delete=False, suffix='.yml')
        self.output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tsv')

    def tearDown(self):
        os.remove(self.input_file1.name)
        os.remove(self.input_file2.name)
        os.remove(self.output_file.name)
    
    def test_identical_files(self):
        content = "key: value"
        self.input_file1.write(content.encode())
        self.input_file2.write(content.encode())
        self.input_file1.close()
        self.input_file2.close()

        with self.assertLogs(level='INFO') as log:
            main(self.input_file1.name, self.input_file2.name, self.output_file.name)

        self.assertIn("INFO:root:The YAML input files are identical.", log.output)
    
    def test_different_files(self):
        pass

    def test_improper_files(self):
        pass