from scripts.compare_tsv import CompareTSV


def main(run_utils, input_file1, input_file2, columns_to_compare):
    comparer = CompareTSV(run_utils, input_file1, input_file2, columns_to_compare)
    if comparer.contains_ID or comparer.replaced_ID:
        comparer.drop_additional_columns()
        comparer.sort_rows()

        if (comparer.df1.shape == comparer.df2.shape):
            comparer.generate_comparison_report()
        else: # Number of rows is not equal
            comparer.make_rows_equal()
            comparer.generate_comparison_report()
    else:
        raise Exception("No variants were found in one or both of the files. Unable to perform comparison.")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
