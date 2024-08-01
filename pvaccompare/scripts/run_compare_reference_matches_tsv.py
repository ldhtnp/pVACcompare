from scripts.run_utils import *
from scripts.compare_reference_matches_tsv import CompareReferenceMatchesTSV



def main(input_file1, input_file2, output_file):
    """
    Purpose:    Control function for the reference matches tsv comparison
    Modifies:   Nothing
    Returns:    None
    """
    comparer = CompareReferenceMatchesTSV(input_file1, input_file2, output_file)
    check_column_formatting(comparer.df1, comparer.df2)

    comparer.create_id_column()
    comparer.common_variants = get_common_variants(comparer.df1, comparer.df2)
    comparer.unique_variants_file1, comparer.unique_variants_file2 = get_unique_variants(comparer.df1, comparer.df2, comparer.common_variants)
    comparer.get_hit_count()

    cols1_to_drop, cols2_to_drop = drop_useless_columns(comparer.df1, comparer.df2, comparer.columns_to_compare)
    output_dropped_cols(cols1_to_drop, cols2_to_drop)
    comparer.columns_to_compare = check_columns_to_compare(comparer.df1, comparer.df2, comparer.columns_to_compare)
    
    if comparer.df1.shape != comparer.df2.shape:
        comparer.df1, comparer.df2 = make_rows_equal(comparer.df1, comparer.df2)
    comparer.generate_comparison_report()



if __name__ == "__main__":
    import sys
    main(sys.argv[1:])