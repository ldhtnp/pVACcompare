import json


class CompareJSON:
    def __init__(self, input_file1, input_file2, output_file):
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.output_path = output_file
        self.json1, self.json2 = self.load_files()
        self.input_differences = {}

    def load_files(self):
        """
        Purpose:    Load the two json metrics files into dictionaries
        Modifies:   Nothing
        Returns:    Two dictionaries corresponding to the two input files
        """
        with open(self.input_file1) as f1, open(self.input_file2) as f2:
            json1 = json.load(f1)
            json2 = json.load(f2)
        return json1, json2

    @staticmethod
    def filter_chr_keys(data):
        """
        Purpose:    Filter the data to remove everything except the inputs
        Modifies:   Nothing
        Returns:    Filtered data
        """
        if isinstance(data, dict):
            return {
                k: CompareJSON.filter_chr_keys(v)
                for k, v in data.items()
                if not k.startswith("chr")
            }
        elif isinstance(data, list):
            return [CompareJSON.filter_chr_keys(item) for item in data]
        else:
            return data

    def compare_metric_data(self):
        """
        Purpose:    Get and store all of the input differences
        Modifies:   self.input_differences
        Returns:    None
        """
        filtered_data1 = self.filter_chr_keys(self.json1)
        filtered_data2 = self.filter_chr_keys(self.json2)

        self.input_differences = {
            "Shared Fields": sorted(
                k for k in filtered_data1.keys() if k in filtered_data2
            ),
            "Fields Unique to File 1": {
                k: v
                for k, v in sorted(filtered_data1.items())
                if k not in filtered_data2
            },
            "Fields Unique to File 2": {
                k: v
                for k, v in sorted(filtered_data2.items())
                if k not in filtered_data1
            },
            "Values Changed": {
                k: f"{filtered_data1[k]} -> {filtered_data2[k]}"
                for k in sorted(filtered_data1)
                if k in filtered_data2 and filtered_data1[k] != filtered_data2[k]
            },
        }

    def generate_input_comparison_report(self):
        """
        Purpose:    Write all of the json metric differences found to the generated report
        Modifies:   Nothing
        Returns:    None
        """
        try:
            with open(self.output_path, "a") as f:
                f.write(
                    "\n============================== METRICS JSON COMPARISON ==============================\n\n\n"
                )
                f.write(f"File 1: {self.input_file1}\n")
                f.write(f"File 2: {self.input_file2}\n")
                f.write("\n--------------------------------\n")
                f.write("\t*** INPUT COMPARISON ***\n")
                f.write("--------------------------------\n")
                for type, changes in self.input_differences.items():
                    if changes:
                        f.write(f"\n=== {type} ===\n")
                        if isinstance(changes, set) or isinstance(changes, list):
                            for key in changes:
                                f.write(f"\t{key}\n")
                        else:
                            for key, value in changes.items():
                                f.write(f"\t{key}:")
                                if isinstance(value, dict):
                                    for field, field_value in value.items():
                                        f.write(f"\n\t\t{field}: {field_value}")
                                elif isinstance(value, list):
                                    for val in value:
                                        f.write(f"\n\t\t{val}")
                                else:
                                    f.write(f" {value}")
                                f.write("\n")
        except Exception as e:
            print(f"Error writing metrics input differences to file: {e}")
