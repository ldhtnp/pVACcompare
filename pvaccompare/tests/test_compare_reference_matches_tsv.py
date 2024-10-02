import unittest
import os
import tempfile
from runners.run_compare_reference_matches_tsv import main


# To run the tests navigate to pvaccompare/ and run the following:
# python -m unittest tests/test_compare_reference_matches_tsv.py
class TestRunCompareReferenceMatchesTSV(unittest.TestCase):
    def setUp(self):
        self.input_file1 = tempfile.NamedTemporaryFile(delete=False, suffix=".tsv")
        self.input_file2 = tempfile.NamedTemporaryFile(delete=False, suffix=".tsv")
        self.output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tsv")
        self.columns_to_compare = ["Peptide", "Match Window"]

    def tearDown(self):
        os.remove(self.input_file1.name)
        os.remove(self.input_file2.name)
        os.remove(self.output_file.name)

    def test_identical_files(self):
        with open("tests/test_data/reference_matches_input1.tsv", "r") as f:
            content = f.read()
        self.input_file1.write(content.encode())
        self.input_file2.write(content.encode())
        self.input_file1.close()
        self.input_file2.close()

        with self.assertLogs(level="INFO") as log:
            main(
                self.input_file1.name,
                self.input_file2.name,
                self.output_file.name,
                self.columns_to_compare,
            )

        self.assertIn(
            "INFO:root:The Reference Matches TSV files are identical.", log.output
        )

    def test_different_files(self):
        with open("tests/test_data/reference_matches_input1.tsv", "r") as f:
            content1 = f.read()
        with open("tests/test_data/reference_matches_input2.tsv", "r") as f:
            content2 = f.read()

        self.input_file1.write(content1.encode())
        self.input_file2.write(content2.encode())
        self.input_file1.close()
        self.input_file2.close()

        main(
            self.input_file1.name,
            self.input_file2.name,
            self.output_file.name,
            self.columns_to_compare,
        )

        self.output_file.seek(0)
        output_content = self.output_file.read().decode()
        sanitized_output = "\n".join(
            [
                line
                for line in output_content.splitlines()
                if not line.startswith("File 1:") and not line.startswith("File 2:")
            ]
        )
        with open(
            "tests/test_data/reference_matches_expected_output_normal.tsv", "r"
        ) as expected_file:
            expected_output = expected_file.read().strip()
        self.assertEqual(sanitized_output.strip(), expected_output)

    def test_duplicate_records(self):
        with open("tests/test_data/reference_matches_input1.tsv", "r") as f:
            content1 = f.read()
        with open("tests/test_data/reference_matches_input3.tsv", "r") as f:
            content2 = f.read()

        self.input_file1.write(content1.encode())
        self.input_file2.write(content2.encode())
        self.input_file1.close()
        self.input_file2.close()

        main(
            self.input_file1.name,
            self.input_file2.name,
            self.output_file.name,
            self.columns_to_compare,
        )

        self.output_file.seek(0)
        output_content = self.output_file.read().decode()
        sanitized_output = "\n".join(
            [
                line
                for line in output_content.splitlines()
                if not line.startswith("File 1:") and not line.startswith("File 2:")
            ]
        )
        with open(
            "tests/test_data/reference_matches_expected_output_duplicates.tsv", "r"
        ) as expected_file:
            expected_output = expected_file.read().strip()
        self.assertEqual(sanitized_output.strip(), expected_output)
