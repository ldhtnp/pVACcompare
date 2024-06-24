import argparse
from scripts.compare_yml import CompareYML


def main(args):
    parser = argparse.ArgumentParser(description="Compare two YAML files and output differences.")
    parser.add_argument("input_file1", help="Path to the first YAML file")
    parser.add_argument("input_file2", help="Path to the second YAML file")
    parser.add_argument("output_file", help="Path to the output TSV file")
    
    parsed_args = parser.parse_args(args)
    file1_path = parsed_args.input_file1
    file2_path = parsed_args.input_file2
    output_path = parsed_args.output_file

    # TODO: Add this as an argument to allow the user to choose which fields to ignore?
    excluded_paths = ["root['input_file']", "root['output_dir']", "root['tmp_dir']"]
    comparer = CompareYML(file1_path, file2_path, output_path, excluded_paths)

    if not comparer.differences:
        print("The YAML files are identical.")
    else:
        comparer.interpret_diff()
        print("Successfully generated input comparison report.")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
