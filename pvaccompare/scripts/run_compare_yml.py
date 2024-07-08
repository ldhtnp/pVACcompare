from scripts.compare_yml import CompareYML


def main(run_utils, input_file1, input_file2):
    comparer = CompareYML(run_utils, input_file1, input_file2)

    if not comparer.differences:
        print("The YAML files are identical.")
    else:
        try:
            comparer.interpret_diff()
            print("Successfully generated input comparison report.")
        except Exception as e:
            print(f"Error occurred while generating input comparison report: {e}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
