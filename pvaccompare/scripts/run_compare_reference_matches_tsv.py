from scripts.run_utils import *
from scripts.compare_reference_matches_tsv import CompareReferenceMatchesTSV



def main(input_file1, input_file2, output_file):
    comparer = CompareReferenceMatchesTSV(input_file1, input_file2, output_file)

    comparer.create_id_column()
    comparer.common_variants = get_common_variants(comparer.df1, comparer.df2)
    comparer.unique_variants_file1, comparer.unique_variants_file2 = get_unique_variants(comparer.df1, comparer.df2, comparer.common_variants)
    comparer.get_hit_count()

    _, _ = drop_useless_columns(comparer.df1, comparer.df2, comparer.columns_to_compare)
    comparer.columns_to_compare = check_columns_to_compare(comparer.df1, comparer.df2, comparer.columns_to_compare)
    
    if comparer.df1.shape != comparer.df2.shape:
        comparer.df1, comparer.df2 = make_rows_equal(comparer.df1, comparer.df2)
    comparer.generate_comparison_report()



if __name__ == "__main__":
    import sys
    main(sys.argv[1:])