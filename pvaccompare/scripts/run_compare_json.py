from scripts.compare_json import CompareJSON


def main(run_utils, input_file1, input_file2):
    comparer = CompareJSON(run_utils, input_file1, input_file2)
    comparer.compare_metric_data()

    if (comparer.input_differences or comparer.variant_differences):
        comparer.write_header()
        if (comparer.input_differences):
            comparer.generate_input_comparison_report()
        else:
            print("The JSON inputs are identical.")
        
        if (comparer.variant_differences):
            comparer.generate_variant_comparison_report()
        else:
            print("The JSON variant data is identical.")
    else:
        print("The JSON metrics files are identical.")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
