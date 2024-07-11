from scripts.compare_aggregated_tsv import CompareAggregatedTSV


def main(run_utils, input_file1, input_file2, columns_to_compare):
    comparer = CompareAggregatedTSV(run_utils, input_file1, input_file2, columns_to_compare)
    if comparer.contains_ID or comparer.replaced_ID:
        comparer.drop_additional_columns()
        comparer.sort_rows()

        if (comparer.df1.shape == comparer.df2.shape):
            comparer.generate_comparison_report()
        else: # Number of rows is not equal
            comparer.df1, comparer.df2 = run_utils.make_rows_equal(comparer.df1, comparer.df2)
            comparer.generate_comparison_report()
    else:
        raise Exception("No variants were found in one or both of the files. Unable to perform comparison.")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
