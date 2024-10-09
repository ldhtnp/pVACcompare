import unittest
import os
import tempfile
from runners.run_compare_aggregated_tsv import main


# To run the tests navigate to pvaccompare/ and run the following:
# python -m unittest tests/test_compare_aggregated_tsv.py
# python -m unittest discover -s tests
class TestRunCompareAggregatedTSV(unittest.TestCase):
    def setUp(self):
        self.input_file1 = tempfile.NamedTemporaryFile(delete=False, suffix=".tsv")
        self.input_file2 = tempfile.NamedTemporaryFile(delete=False, suffix=".tsv")
        self.output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tsv")
        self.columns_to_compare = [
            "Num Passing Transcripts",
            "Best Peptide",
            "Best Transcript",
            "Num Passing Peptides",
            "Tier",
        ]

    def tearDown(self):
        os.remove(self.input_file1.name)
        os.remove(self.input_file2.name)
        os.remove(self.output_file.name)

    def test_identical_files(self):
        with open("tests/test_data/aggregated_input1.tsv", "r") as f:
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

        self.assertIn("INFO:root:The Aggregated TSV files are identical.", log.output)

    def test_different_files(self):
        with open("tests/test_data/aggregated_input1.tsv", "r") as f:
            content1 = f.read()
        with open("tests/test_data/aggregated_input2.tsv", "r") as f:
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
            "tests/test_data/aggregated_expected_output.tsv", "r"
        ) as expected_file:
            expected_output = expected_file.read().strip()
        self.assertEqual(sanitized_output.strip(), expected_output)

    def test_missing_id(self):
        with open("tests/test_data/aggregated_input1.tsv", "r") as f:
            content1 = f.read()
        with open("tests/test_data/aggregated_input3.tsv", "r") as f:
            content2 = f.read()

        self.input_file1.write(content1.encode())
        self.input_file2.write(content2.encode())
        self.input_file1.close()
        self.input_file2.close()

        with self.assertLogs(level="INFO") as log:
            main(
                self.input_file1.name,
                self.input_file2.name,
                self.output_file.name,
                self.columns_to_compare,
            )
        self.assertIn("INFO:root:• Replaced ID with Gene and AA Change", log.output)

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
            "tests/test_data/aggregated_id_change_output.tsv", "r"
        ) as expected_file:
            expected_output = expected_file.read().strip()
        self.assertEqual(sanitized_output.strip(), expected_output)
