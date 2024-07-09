from scripts.compare_json import CompareJSON


def main(run_utils, input_file1, input_file2):
    comparer = CompareJSON(run_utils, input_file1, input_file2)
    comparer.compare_metric_inputs()
    if (comparer.input_differences):
        comparer.write_header()
        comparer.generate_input_comparison_report()
    else:
        print("The JSON files are identical.")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
