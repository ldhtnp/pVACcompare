import argparse
from scripts.compare_tsv import CompareTSV

def main(args):
    parser = argparse.ArgumentParser(description="Compare two TSV files and output differences.")
    parser.add_argument("input_file1", help="Path to the first TSV file")
    parser.add_argument("input_file2", help="Path to the second TSV file")
    parser.add_argument("output_file", help="Path to the output TSV file")
    
    parsed_args = parser.parse_args(args)
    file1_path = parsed_args.input_file1
    file2_path = parsed_args.input_file2
    output_path = parsed_args.output_file

    # Susanna stated number of variants, best peptide selected, best transcript select, and tier
    # TODO: Add this as a parameter to the command?
    columns_to_compare = ['ID', 'Best Peptide', 'Tier']

    comparer = CompareTSV(file1_path, file2_path, output_path, columns_to_compare)
    comparer.drop_additional_columns()
    comparer.sort_rows()

    if (comparer.df1.shape == comparer.df2.shape):
        comparer.compare_dataframes()
    else: # Number of rows is not equal
        comparer.drop_additional_rows()

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
