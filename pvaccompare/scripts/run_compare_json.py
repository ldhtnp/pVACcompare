import argparse
from deepdiff import DeepDiff
import json
import re


class CompareJSON():
    def __init__(self, input_file1, input_file2, output_path):
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.json1, self.json2 = self.load_files()
        self.output_path = output_path
        self.differences = self.run_diff()
        self.output_mappings = {
            'dictionary_item_added': 'Fields Unique to File 2',
            'dictionary_item_removed': 'Fields Unique to File 1',
            'values_changed': 'Values Changed',
            'iterable_item_added': 'Values Added in File 2',
            #'type_changes': 'Type Change'
        }

    
    def load_files(self):
        with open(self.input_file1) as f1, open(self.input_file2) as f2:
            json1 = json.load(f1)
            json2 = json.load(f2)
        return json1, json2

    
    def run_diff(self):
        diff = DeepDiff(
            self.json1,
            self.json2,
            ignore_order=True,  # Ignore order of lists
            report_repetition=True,  # Report repetitions
            significant_digits=5,  # Set significant digits for numeric comparison
            ignore_type_in_groups=[(str, int), (str, float)]
        )
        return diff
    

    def generate_report(self):
        with open(self.output_path, 'w') as f:
            f.write(f"File 1: {self.input_file1}\n")
            f.write(f"File 2: {self.input_file2}\n\n")
            for change_type, changes in self.differences.items():
                f.write(f"=== {self.output_mappings[change_type]} ===\n")
                pattern = r"root\['(.*?)'\]"
                if isinstance(changes, dict):
                    for change, details in changes.items():
                        formatted_output = re.match(pattern, change)[1]
                        if change_type == "values_changed":
                            f.write(f"\t{formatted_output}: {details['old_value']} -> {details['new_value']}\n")
                        elif change_type in ["dictionary_item_added", "dictionary_item_removed"]:
                            f.write(f"\t{formatted_output}: {details}\n")
                        elif change_type == "type_changes":
                            f.write(f"\t{formatted_output}: {details['old_type']} -> {details['new_type']}\n")
                        elif change_type in ["iterable_item_added", "iterable_item_removed"]:
                            f.write(f"\t{formatted_output}: {details}\n")
                else:
                    changes = str(changes)
                    matches = re.findall(pattern, changes)
                    formatted_output = "\n\t".join(matches)
                    f.write(f"\t{formatted_output}\n")
                f.write("\n")


def main(args):
    parser = argparse.ArgumentParser(description="Compare two json files and output differences.")
    parser.add_argument("input_file1", help="Path to the first json file")
    parser.add_argument("input_file2", help="Path to the second json file")
    parser.add_argument("output_file", help="Path to the output file")
    
    parsed_args = parser.parse_args(args)
    file1_path = parsed_args.input_file1
    file2_path = parsed_args.input_file2
    output_path = parsed_args.output_file

    comparer = CompareJSON(file1_path, file2_path, output_path)
    if (comparer.differences):
        comparer.generate_report()
        print("Successfully generated JSON comparison report.")
    else:
        print("The JSON files are identical.")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
