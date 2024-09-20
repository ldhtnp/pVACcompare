from comparisons import CompareJSON


def main(input_file1, input_file2, output_file):
    """
    Purpose:    Control function for the metrics json file comparison
    Modifies:   Nothing
    Returns:    None
    """
    comparer = CompareJSON(input_file1, input_file2, output_file)
    comparer.compare_metric_data()

    if any(
        key != "Shared Fields" and comparer.input_differences[key]
        for key in comparer.input_differences
    ):
        comparer.generate_input_comparison_report()
    else:
        print("The JSON metric inputs are identical.")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
