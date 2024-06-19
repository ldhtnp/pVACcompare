import yaml
from deepdiff import DeepDiff
import argparse


class CompareYML():
    def __init__(self, input_file1, input_file2, output_path, excluded_paths):
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.data1, self.data2 = self.load_files()
        self.output_path = output_path
        self.differences = DeepDiff(self.data1, self.data2, ignore_order=True, exclude_paths=excluded_paths)


    def load_files(self):
        with open(self.input_file1, 'r') as f1, open(self.input_file2, 'r') as f2:
            data1 = yaml.safe_load(f1)
            data2 = yaml.safe_load(f2)
        return data1, data2


    def interpret_diff(self):
        with open(self.output_path, 'w') as f:
            for change_type, changes in self.differences.items():
                f.write(f"Change type: {change_type}\n")
                if isinstance(changes, dict):
                    for change, details in changes.items():
                        if change_type == "values_changed":
                            f.write(f"  {change}: {details['old_value']} -> {details['new_value']}\n")
                        elif change_type in ["dictionary_item_added", "dictionary_item_removed"]:
                            f.write(f"  {change}: {details}\n")
                        elif change_type == "type_changes":
                            f.write(f"  {change}: {details['old_type']} -> {details['new_type']}\n")
                        elif change_type in ["iterable_item_added", "iterable_item_removed"]:
                            f.write(f"  {change}: {details}\n")
                else:
                    f.write(f"  {changes}\n")


def main(args):
    parser = argparse.ArgumentParser(description="Compare two YAML files and output differences.")
    parser.add_argument("input_file1", help="Path to the first YAML file")
    parser.add_argument("input_file2", help="Path to the second YAML file")
    parser.add_argument("output_file", help="Path to the output TSV file")
    
    parsed_args = parser.parse_args(args)
    file1_path = parsed_args.input_file1
    file2_path = parsed_args.input_file2
    output_path = parsed_args.output_file

    excluded_paths = ["root['input_file']", "root['output_dir']", "root['tmp_dir']"]
    comparer = CompareYML(file1_path, file2_path, output_path, excluded_paths)

    if not comparer.differences:
        print("The YAML files are identical.")
    else:
        comparer.interpret_diff()


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
