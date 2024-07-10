import json
import re


class CompareJSON():
    def __init__(self, run_utils, input_file1, input_file2):
        self.run_utils = run_utils
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.json1, self.json2 = self.load_files()
        self.output_path = run_utils.output_path
        self.contains_reference_match = self.check_contain_reference_match()
        self.input_differences = {}
        self.variant_differences = {}

    
    def load_files(self):
        with open(self.input_file1) as f1, open(self.input_file2) as f2:
            json1 = json.load(f1)
            json2 = json.load(f2)
        return json1, json2
    

    def filter_chr_keys(self, data):
        filtered_data = {}
        chr_data = {}
        for k, v in data.items():
            if k.startswith('chr'):
                if k in self.run_utils.common_rows:
                    chr_data[k] = v
            else:
                filtered_data[k] = v
        return filtered_data, chr_data
    

    def compare_metric_data(self):
        input_data1, variant_data1 = self.filter_chr_keys(self.json1)
        input_data2, variant_data2 = self.filter_chr_keys(self.json2)

        self.input_differences = {
            'Shared Fields': {k for k in input_data1.keys() if k in input_data2},
            'Fields Unique to File 1': {k: v for k, v in input_data1.items() if k not in input_data2},
            'Fields Unique to File 2': {k: v for k, v in input_data2.items() if k not in input_data1},
            'Values Changed': {k: f"{input_data1[k]} -> {input_data2[k]}" for k in input_data1 if k in input_data2 and input_data1[k] != input_data2[k]}
        }

        self.variant_differences = {
            'Fields Unique to File 1': {k: v for k, v in variant_data1.items() if k not in variant_data2},
            'Fields Unique to File 2': {k: v for k, v in variant_data2.items() if k not in variant_data1},
            'Values Changed': {k: f"{variant_data1[k]} -> {variant_data2[k]}" for k in variant_data1 if k in variant_data2 and variant_data1[k] != variant_data2[k]}
        }
    

    def generate_input_comparison_report(self):
        try:
            with open(self.output_path, 'a') as f:
                f.write("\n--------------------------------\n")
                f.write("\t*** INPUT COMPARISON ***\n")
                f.write("--------------------------------\n")
                for type, changes in self.input_differences.items():
                    if changes:
                        f.write(f"\n=== {type} ===\n")
                        if isinstance(changes, set):
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
                                f.write('\n')
        except Exception as e:
            print(f"Error writing metrics input differences to file: {e}")
    

    def generate_variant_comparison_report(self):
        pass


    def check_contain_reference_match(self):
        pattern = re.compile('"reference_matches"')
        return bool(pattern.search(json.dumps(self.json1)) and pattern.search(json.dumps(self.json2)))

    
    def write_header(self):
        try:
            with open(self.output_path, 'a') as f:
                f.write("\n\n============================== METRICS JSON COMPARISON ==============================\n\n\n")
                f.write(f"File 1: {self.input_file1}\n")
                f.write(f"File 2: {self.input_file2}\n")
        except Exception as e:
            print(f"Error writing metrics header to file: {e}")