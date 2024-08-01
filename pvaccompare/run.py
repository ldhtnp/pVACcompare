import argparse
import glob
import os
from scripts import run_compare_aggregated_tsv
from scripts import run_compare_unaggregated_tsv
from scripts import run_compare_reference_matches_tsv
from scripts import run_compare_yml
from scripts import run_compare_json


# TODO: Add summary to unaggregated output and reference matches output?

def define_parser():
    """
    Purpose:    Define arguments for the parser that the user can use
    Modifies:   Nothing
    Returns:    The parser
    """
    valid_columns = ["Gene", "AA Change", "Num Passing Transcripts", "Best Peptide", "Best Transcript", "Num Passing Peptides", "IC50 MT", "IC50 WT", "%%ile MT", "%%ile WT", "RNA Expr", "RNA VAF", "DNA VAF", "Tier"]
    default_columns = ["Num Passing Transcripts", "Best Peptide", "Best Transcript", "Num Passing Peptides", "Tier"]

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('results_folder1', help="Path to first results input folder")
    parser.add_argument('results_folder2', help="Path to second results input folder")
    parser.add_argument('output_file', help="Name for generated report")
    parser.add_argument('--mhc_class', choices=['1', '2'], help="Specify MHC class 1 or class 2")
    parser.add_argument('--columns_to_compare', type=lambda s:[a for a in s.split(',')], default=default_columns,
                        help=f"Comma-separated columns to include in the TSV comparison, choices: {', '.join(valid_columns)}")
    return parser



def validate_columns(columns_to_compare, parser):
    """
    Purpose:    Makes sure the user inputs valid columns
    Modifies:   Nothing
    Returns:    None
    """
    valid_columns = ["Gene", "AA Change", "Num Passing Transcripts", "Best Peptide", "Best Transcript", "Num Passing Peptides", "IC50 MT", "IC50 WT", "%ile MT", "%ile WT", "RNA Expr", "RNA VAF", "DNA VAF", "Tier"]
    for col in columns_to_compare:
        if col not in valid_columns:
            parser.error(f"Invalid column '{col}' specified.\nValid columns are: {', '.join(valid_columns)}")



def find_file(results_folder, subfolder, pattern):
    """
    Purpose:    Attempts to locate the files needed for each comparison
    Modifies:   Nothing
    Returns:    A string of the file path
    """
    search_path = os.path.join(results_folder, subfolder, pattern)
    files = glob.glob(search_path, recursive=True)
    return files[0] if files else None



def run_comparison(prefix, results_folder1, results_folder2, output_file, columns_to_compare):
    """
    Purpose:    Runs all of the different comparisons
    Modifies:   Nothing
    Returns:    None
    """
    output_file = output_file + '_' + prefix + '.tsv'

    yml1_path = find_file(results_folder1, prefix + '/log', 'inputs.yml')
    yml2_path = find_file(results_folder2, prefix + '/log', 'inputs.yml')
    if yml1_path and yml2_path:
        print("Running the input YML comparison tool...")
        run_compare_yml.main(yml1_path, yml2_path, output_file)
        print(u'\u2713 Comparison completed successfully.')
    else:
        if yml1_path:
            print(f"ERROR: Could not locate the input YML file in results folder 2 for {prefix.replace('_', ' ')}.")
        elif yml2_path:
            print(f"ERROR: Could not locate the input YML file in results folder 1 for {prefix.replace('_', ' ')}.")
        else:
            print(f"ERROR: Could not locate the input YML file in either results folder for {prefix.replace('_', ' ')}.")
        print(u'\u2716 Comparison skipped.')
    
    json1_path = find_file(results_folder1, prefix + '/', '*all_epitopes.aggregated.metrics.json')
    json2_path = find_file(results_folder2, prefix + '/', '*all_epitopes.aggregated.metrics.json')
    if json1_path and json2_path:
        print("\nRunning the metrics JSON comparison tool...")
        run_compare_json.main(json1_path, json2_path, output_file)
        print(u'\u2713 Comparison completed successfully.')
    else:
        if json1_path:
            print(f"\nERROR: Could not locate the metrics JSON file in results folder 2 for {prefix.replace('_', ' ')}.")
        elif json2_path:
            print(f"\nERROR: Could not locate the metrics JSON file in results folder 1 for {prefix.replace('_', ' ')}.")
        else:
            print(f"\nERROR: Could not locate the metrics JSON file in either results folder for {prefix.replace('_', ' ')}.")
        print(u'\u2716 Comparison skipped.')

    agg_tsv1_path = find_file(results_folder1, prefix + '/', '*all_epitopes.aggregated.tsv')
    agg_tsv2_path = find_file(results_folder2, prefix + '/', '*all_epitopes.aggregated.tsv')
    if agg_tsv1_path and agg_tsv2_path:
        print("\nRunning the aggregated TSV comparison tool...")
        run_compare_aggregated_tsv.main(agg_tsv1_path, agg_tsv2_path, output_file, columns_to_compare)
        print(u'\u2713 Comparison completed successfully.')
    else:
        if agg_tsv1_path:
            print(f"\nERROR: Could not locate the aggregated TSV file in results folder 2 for {prefix.replace('_', ' ')}.")
        elif agg_tsv2_path:
            print(f"\nERROR: Could not locate the aggregated TSV file in results folder 1 for {prefix.replace('_', ' ')}.")
        else:
            print(f"\nERROR: Could not locate the aggregated TSV file in either results folder for {prefix.replace('_', ' ')}.")
        print(u'\u2716 Comparison skipped.')
    
    unagg_tsv1_path = find_file(results_folder1, prefix + '/', '*all_epitopes.tsv')
    unagg_tsv2_path = find_file(results_folder2, prefix + '/', '*all_epitopes.tsv')
    if unagg_tsv1_path and unagg_tsv2_path:
        print("\nRunning the unaggregated TSV comparison tool...")
        run_compare_unaggregated_tsv.main(unagg_tsv1_path, unagg_tsv2_path, output_file)
        print(u'\u2713 Comparison completed successfully.')
    else:
        if unagg_tsv1_path:
            print(f"\nERROR: Could not locate the unaggregated TSV file in results folder 2 for {prefix.replace('_', ' ')}.")
        elif unagg_tsv2_path:
            print(f"\nERROR: Could not locate the unaggregated TSV file in results folder 1 for {prefix.replace('_', ' ')}.")
        else:
            print(f"\nERROR: Could not locate the unaggregated TSV file in either results folder for {prefix.replace('_', ' ')}.")
        print(u'\u2716 Comparison skipped.')
    
    refmatch_tsv1_path = find_file(results_folder1, prefix + '/', '*.reference_matches')
    refmatch_tsv2_path = find_file(results_folder2, prefix + '/', '*.reference_matches')
    if refmatch_tsv1_path and refmatch_tsv2_path:
        print("\nRunning the reference match TSV comparison tool...")
        run_compare_reference_matches_tsv.main(refmatch_tsv1_path, refmatch_tsv2_path, output_file)
        print(u'\u2713 Comparison completed successfully.')
    else:
        if refmatch_tsv1_path:
            print(f"\nERROR: Could not locate the reference match TSV file in results folder 2 for {prefix.replace('_', ' ')}.")
        elif refmatch_tsv2_path:
            print(f"\nERROR: Could not locate the reference match TSV file in results folder 1 for {prefix.replace('_', ' ')}.")
        else:
            print(f"\nERROR: Could not locate the reference match TSV file in either results folder for {prefix.replace('_', ' ')}.")
        print(u'\u2716 Comparison skipped.')
    print('\n' + u'\u2500'*55)
    print(f"Successfully generated {prefix.replace('_', ' ')} comparison report.")
    print(u'\u2500'*55)



def main():
    parser = define_parser()
    args = parser.parse_args()

    validate_columns(args.columns_to_compare, parser)

    classes_to_run = [args.mhc_class] if args.mhc_class else ['1', '2']

    for class_type in classes_to_run:
        if class_type == '1':
            prefix = "MHC_Class_I"
        elif class_type == '2':
            prefix = "MHC_Class_II"
        run_comparison(prefix, args.results_folder1, args.results_folder2, args.output_file, args.columns_to_compare)



if __name__ == '__main__':
    main()