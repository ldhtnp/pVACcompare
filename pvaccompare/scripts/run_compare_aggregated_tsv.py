from scripts.compare_aggregated_tsv import CompareAggregatedTSV
from scripts.run_utils import *



def main(input_file1, input_file2, output_file, columns_to_compare):
    """
    Purpose:    Control function for the aggregated tsv file comparison
    Modifies:   Nothing
    Returns:    None
    """
    comparer = CompareAggregatedTSV(input_file1, input_file2, output_file, columns_to_compare)
    check_column_formatting(comparer.df1, comparer.df2)
    comparer.columns_to_compare = comparer.check_columns()
    
    comparer.common_variants = get_common_variants(comparer.df1, comparer.df2)
    comparer.unique_variants_file1, comparer.unique_variants_file2 = get_unique_variants(comparer.df1, comparer.df2, comparer.common_variants)

    if (comparer.df1.shape == comparer.df2.shape):
        comparer.generate_comparison_report()
    else: # Number of rows is not equal
        comparer.df1, comparer.df2 = make_rows_equal(comparer.df1, comparer.df2)
        comparer.generate_comparison_report()



if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
