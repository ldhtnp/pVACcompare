from scripts.compare_tsv import CompareTSV


def main(run_utils, input_file1, input_file2):
    # Number of variants, best peptide selected, best transcript select, and tier most important
    # TODO: Add this as a parameter to the command?
    columns_to_compare = ['ID', 'Best Transcript', 'Best Peptide', 'Tier', 'Num Passing Transcripts', 'Num Passing Peptides']

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
