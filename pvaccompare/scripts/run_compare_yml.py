import yaml
import argparse


class CompareYML():
    def __init__(self, input_file1, input_file2, output_path):
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.output_path = output_path

def main(args):
    parser = argparse.ArgumentParser(description="Compare two YAML files and output differences.")
    parser.add_argument("input_file1", help="Path to the first YAML file")
    parser.add_argument("input_file2", help="Path to the second YAML file")
    parser.add_argument("output_file", help="Path to the output TSV file")
    
    parsed_args = parser.parse_args(args)
    file1_path = parsed_args.input_file1
    file2_path = parsed_args.input_file2
    output_path = parsed_args.output_file
    
    with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
        data1 = yaml.safe_load(f1)
        data2 = yaml.safe_load(f2)

    # Compare the two YAML files
    if data1 == data2:
        print("The YAML files are identical.")
    else:
        print("Differences between the YAML files:")
        print(yaml.dump(data1, default_flow_style=False))
        print("---")
        print(yaml.dump(data2, default_flow_style=False))

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
