from scripts.compare_aggregated_tsv import CompareAggregatedTSV
from scripts.run_utils import *



def main(input_file1, input_file2, output_file, columns_to_compare):
    """
    Purpose:    Control function for the aggregated tsv file comparison
    Modifies:   Nothing
    Returns:    None
    """
    id_format = "Chromosome-Start-Stop-Reference-Variant"

    comparer = CompareAggregatedTSV(input_file1, input_file2, output_file, columns_to_compare)
    check_column_formatting(comparer.df1, comparer.df2)

    cols1_to_drop, cols2_to_drop = drop_useless_columns(comparer.df1, comparer.df2, comparer.columns_to_compare)
    columns_dropped_message = output_dropped_cols(cols1_to_drop, cols2_to_drop)
    comparer.columns_to_compare = check_columns_to_compare(comparer.df1, comparer.df2, comparer.columns_to_compare)
    comparer.check_id(cols1_to_drop, cols2_to_drop)
    
    common_variants = get_common_variants(comparer.df1, comparer.df2)
    unique_variants_file1, unique_variants_file2 = get_unique_variants(comparer.df1, comparer.df2, common_variants)

    if (comparer.df1.shape != comparer.df2.shape):
        comparer.df1, comparer.df2 = make_rows_equal(comparer.df1, comparer.df2)
    differences, unique_variants = get_file_differences(comparer.df1, comparer.df2, comparer.columns_to_compare, unique_variants_file1, unique_variants_file2, comparer.contains_id)
    differences_summary = generate_differences_summary(common_variants, unique_variants_file1, unique_variants_file2, differences)
    generate_comparison_report("Aggregated TSV", id_format, differences, unique_variants, comparer.input_file1, comparer.input_file2, comparer.output_path, columns_dropped_message, differences_summary, comparer.replaced_id)



if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
