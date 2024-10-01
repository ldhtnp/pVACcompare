import unittest
import os
import tempfile
from runners.run_compare_yml import main


# To run the tests navigate to pvaccompare/ and run the following:
# python -m unittest tests/test_compare_yml.py
class TestRunCompareYML(unittest.TestCase):
    def setUp(self):
        self.input_file1 = tempfile.NamedTemporaryFile(delete=False, suffix=".yml")
        self.input_file2 = tempfile.NamedTemporaryFile(delete=False, suffix=".yml")
        self.output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tsv")

    def tearDown(self):
        os.remove(self.input_file1.name)
        os.remove(self.input_file2.name)
        os.remove(self.output_file.name)

    def test_identical_files(self):
        with open("tests/test_data/yml_input1.yml", "r") as f:
            content = f.read()
        self.input_file1.write(content.encode())
        self.input_file2.write(content.encode())
        self.input_file1.close()
        self.input_file2.close()

        with self.assertLogs(level="INFO") as log:
            main(self.input_file1.name, self.input_file2.name, self.output_file.name)

        self.assertIn("INFO:root:The YAML input files are identical.", log.output)

    def test_different_files(self):

        with open("tests/test_data/yml_input1.yml", "r") as f:
            content1 = f.read()

        with open("tests/test_data/yml_input2.yml", "r") as f:
            content2 = f.read()

        self.input_file1.write(content1.encode())
        self.input_file2.write(content2.encode())
        self.input_file1.close()
        self.input_file2.close()

        main(self.input_file1.name, self.input_file2.name, self.output_file.name)

        self.output_file.seek(0)
        output_content = self.output_file.read().decode()
        sanitized_output = "\n".join(
            [
                line
                for line in output_content.splitlines()
                if not line.startswith("File 1:") and not line.startswith("File 2:")
            ]
        )
        with open("tests/test_data/yml_expected_output.tsv", "r") as expected_file:
            expected_output = expected_file.read().strip()

        self.assertEqual(sanitized_output.strip(), expected_output)
