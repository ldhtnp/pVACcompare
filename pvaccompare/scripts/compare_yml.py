import yaml
from deepdiff import DeepDiff
import datetime
import re



class CompareYML():
    def __init__(self, input_file1, input_file2, output_file):
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.output_path = output_file
        self.data1, self.data2 = self.load_files()
        self.differences = DeepDiff(self.data1, self.data2, ignore_order=True)
        self.output_mappings = {
            'dictionary_item_added': 'Fields Unique to File 2',
            'dictionary_item_removed': 'Fields Unique to File 1',
            'values_changed': 'Values Changed',
            'iterable_item_added': 'Values Added in File 2'
        }



    def load_files(self):
        """
        Purpose:    Load the two input yml files into dictionaries
        Modifies:   Nothing
        Returns:    Two dictionaries corresponding to the two input files
        """
        with open(self.input_file1, 'r') as f1, open(self.input_file2, 'r') as f2:
            data1 = yaml.safe_load(f1)
            data2 = yaml.safe_load(f2)
        return data1, data2



    def interpret_diff(self):
        """
        Purpose:    Write all of the input yml differences found to the generated report
        Modifies:   Nothing
        Returns:    None
        """
        with open(self.output_path, 'w') as f:
            f.write(f"Report Generation Date and Time: {datetime.datetime.now()}\n")
            f.write("\n\n============================== INPUT YML COMPARISON ==============================\n\n\n")
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