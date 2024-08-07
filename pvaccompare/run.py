import argparse
import glob
import os
from scripts import run_compare_aggregated_tsv
from scripts import run_compare_unaggregated_tsv
from scripts import run_compare_reference_matches_tsv
from scripts import run_compare_yml
from scripts import run_compare_json



def define_parser():
    """
    Purpose:    Define arguments for the parser that the user can use
    Modifies:   Nothing
    Returns:    The parser
    """
    valid_aggregated_columns = ["Gene", "AA Change", "Num Passing Transcripts", "Best Peptide", "Best Transcript", "Num Passing Peptides",
                                "IC50 MT", "IC50 WT", "%%ile MT", "%%ile WT", "RNA Expr", "RNA VAF", "DNA VAF", "Tier"]
    valid_unaggregated_columns = ['Biotype', 'Sub-peptide Position', 'Median MT IC50 Score', 'Median WT IC50 Score', 'Median MT Percentile', 
                                    'Median WT Percentile', 'WT Epitope Seq', 'Tumor DNA VAF', 'Tumor RNA Depth', 'Tumor RNA VAF',
                                    'Gene Expression', 'BigMHC_EL WT Score', 'BigMHC_EL MT Score', 'BigMHC_IM WT Score', 'BigMHC_IM MT Score',
                                    'MHCflurryEL Processing WT Score', 'MHCflurryEL Processing MT Score', 'MHCflurryEL Presentation WT Score',
                                    'MHCflurryEL Presentation MT Score', 'MHCflurryEL Presentation WT Percentile', 'MHCflurryEL Presentation MT Percentile',
                                    'MHCflurry WT IC50 Score', 'MHCflurry MT IC50 Score', 'MHCflurry WT Percentile', 'MHCflurry MT Percentile',
                                    'MHCnuggetsI WT IC50 Score', 'MHCnuggetsI MT IC50 Score', 'MHCnuggetsI WT Percentile', 'MHCnuggetsI MT Percentile',
                                    'NetMHC WT IC50 Score', 'NetMHC MT IC50 Score', 'NetMHC WT Percentile', 'NetMHC MT Percentile', 'NetMHCcons WT IC50 Score',
                                    'NetMHCcons MT IC50 Score', 'NetMHCcons WT Percentile', 'NetMHCcons MT Percentile', 'NetMHCpan WT IC50 Score',
                                    'NetMHCpan MT IC50 Score', 'NetMHCpan WT Percentile', 'NetMHCpan MT Percentile', 'NetMHCpanEL WT Score',
                                    'NetMHCpanEL MT Score', 'NetMHCpanEL WT Percentile', 'NetMHCpanEL MT Percentile', 'PickPocket WT IC50 Score',
                                    'PickPocket MT IC50 Score', 'PickPocket WT Percentile', 'PickPocket MT Percentile', 'SMM WT IC50 Score', 'SMM MT IC50 Score',
                                    'SMM WT Percentile', 'SMM MT Percentile', 'SMMPMBEC WT IC50 Score', 'SMMPMBEC MT IC50 Score', 'SMMPMBEC WT Percentile',
                                    'SMMPMBEC MT Percentile', 'DeepImmuno WT Score', 'DeepImmuno MT Score', 'Problematic Positions']
    valid_reference_match_columns = ['Peptide', 'Hit Definition', 'Match Window', 'Match Sequence']

    default_aggregated_columns = ["Num Passing Transcripts", "Best Peptide", "Best Transcript", "Num Passing Peptides", "Tier"]
    default_unaggregated_columns = ['Biotype', 'Sub-peptide Position', 'Median MT IC50 Score', 'Median WT IC50 Score', 'Median MT Percentile', 
                                    'Median WT Percentile', 'WT Epitope Seq', 'Tumor DNA VAF', 'Tumor RNA Depth', 'Tumor RNA VAF', 'Gene Expression']
    default_reference_match_columns = ['Peptide', 'Match Window']

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('results_folder1', help="Path to first results input folder")
    parser.add_argument('results_folder2', help="Path to second results input folder")
    parser.add_argument('output_file', help="Name for generated report")
    parser.add_argument('--mhc_class', choices=['1', '2'], help="Specify MHC class 1 or class 2")
    parser.add_argument('--aggregated_columns', type=lambda s:[a for a in s.split(',')], default=default_aggregated_columns,
                        help=f"Comma-separated columns to include in the aggregated TSV comparison, choices: {', '.join(valid_aggregated_columns)}")
    parser.add_argument('--unaggregated_columns', type=lambda s:[a for a in s.split(',')], default=default_unaggregated_columns,
                        help=f"Comma-separated columns to include in the unaggregated TSV comparison, choices: {', '.join(valid_unaggregated_columns)}")
    parser.add_argument('--reference_match_columns', type=lambda s:[a for a in s.split(',')], default=default_reference_match_columns,
                        help=f"Comma-separated columns to include in the reference match TSV comparison, choices: {', '.join(valid_reference_match_columns)}")
    return parser



def validate_aggregated_columns(aggregated_columns, parser):
    """
    Purpose:    Makes sure the user inputs valid aggregated tsv columns
    Modifies:   Nothing
    Returns:    None
    """
    valid_aggregated_columns = ["Gene", "AA Change", "Num Passing Transcripts", "Best Peptide", "Best Transcript", "Num Passing Peptides", "IC50 MT", "IC50 WT", "%ile MT", "%ile WT", "RNA Expr", "RNA VAF", "DNA VAF", "Tier"]
    for col in aggregated_columns:
        if col not in valid_aggregated_columns:
            parser.error(f"Invalid aggregated column '{col}' specified.\nValid columns are: {', '.join(valid_aggregated_columns)}")



def validate_unaggregated_columns(unaggregated_columns, parser):
    """
    Purpose:    Makes sure the user inputs valid unaggregated tsv columns
    Modifies:   Nothing
    Returns:    None
    """
    valid_unaggregated_columns = ['Biotype', 'Sub-peptide Position', 'Median MT IC50 Score', 'Median WT IC50 Score', 'Median MT Percentile', 
                                    'Median WT Percentile', 'WT Epitope Seq', 'Tumor DNA VAF', 'Tumor RNA Depth', 'Tumor RNA VAF',
                                    'Gene Expression', 'BigMHC_EL WT Score', 'BigMHC_EL MT Score', 'BigMHC_IM WT Score', 'BigMHC_IM MT Score',
                                    'MHCflurryEL Processing WT Score', 'MHCflurryEL Processing MT Score', 'MHCflurryEL Presentation WT Score',
                                    'MHCflurryEL Presentation MT Score', 'MHCflurryEL Presentation WT Percentile', 'MHCflurryEL Presentation MT Percentile',
                                    'MHCflurry WT IC50 Score', 'MHCflurry MT IC50 Score', 'MHCflurry WT Percentile', 'MHCflurry MT Percentile',
                                    'MHCnuggetsI WT IC50 Score', 'MHCnuggetsI MT IC50 Score', 'MHCnuggetsI WT Percentile', 'MHCnuggetsI MT Percentile',
                                    'NetMHC WT IC50 Score', 'NetMHC MT IC50 Score', 'NetMHC WT Percentile', 'NetMHC MT Percentile', 'NetMHCcons WT IC50 Score',
                                    'NetMHCcons MT IC50 Score', 'NetMHCcons WT Percentile', 'NetMHCcons MT Percentile', 'NetMHCpan WT IC50 Score',
                                    'NetMHCpan MT IC50 Score', 'NetMHCpan WT Percentile', 'NetMHCpan MT Percentile', 'NetMHCpanEL WT Score',
                                    'NetMHCpanEL MT Score', 'NetMHCpanEL WT Percentile', 'NetMHCpanEL MT Percentile', 'PickPocket WT IC50 Score',
                                    'PickPocket MT IC50 Score', 'PickPocket WT Percentile', 'PickPocket MT Percentile', 'SMM WT IC50 Score', 'SMM MT IC50 Score',
                                    'SMM WT Percentile', 'SMM MT Percentile', 'SMMPMBEC WT IC50 Score', 'SMMPMBEC MT IC50 Score', 'SMMPMBEC WT Percentile',
                                    'SMMPMBEC MT Percentile', 'DeepImmuno WT Score', 'DeepImmuno MT Score', 'Problematic Positions']
    for col in unaggregated_columns:
        if col not in valid_unaggregated_columns:
            parser.error(f"Invalid unaggregated column '{col}' specified.\nValid columns are: {', '.join(valid_unaggregated_columns)}")



def validate_reference_match_columns(reference_match_columns, parser):
    """
    Purpose:    Makes sure the user inputs valid reference match tsv columns
    Modifies:   Nothing
    Returns:    None
    """
    valid_reference_match_columns = ['Peptide', 'Hit Definition', 'Match Window', 'Match Sequence']
    for col in reference_match_columns:
        if col not in valid_reference_match_columns:
            parser.error(f"Invalid reference match column '{col}' specified.\nValid columns are: {', '.join(valid_reference_match_columns)}")



def find_file(results_folder, subfolder, pattern):
    """
    Purpose:    Attempts to locate the files needed for each comparison
    Modifies:   Nothing
    Returns:    A string of the file path
    """
    search_path = os.path.join(results_folder, subfolder, pattern)
    files = glob.glob(search_path, recursive=True)
    return files[0] if files else None



def run_comparison(prefix, results_folder1, results_folder2, output_file, aggregated_columns, unaggregated_columns, reference_match_columns):
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
        run_compare_aggregated_tsv.main(agg_tsv1_path, agg_tsv2_path, output_file, aggregated_columns)
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
        run_compare_unaggregated_tsv.main(unagg_tsv1_path, unagg_tsv2_path, output_file, unaggregated_columns)
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
        run_compare_reference_matches_tsv.main(refmatch_tsv1_path, refmatch_tsv2_path, output_file, reference_match_columns)
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
    """
    Purpose:    Control function for the whole tool, calls run_comparison which calls all of the comparisons
    Modifies:   Nothing
    Returns:    None
    """
    parser = define_parser()
    args = parser.parse_args()

    validate_aggregated_columns(args.aggregated_columns, parser)
    validate_unaggregated_columns(args.unaggregated_columns, parser)
    validate_reference_match_columns(args.reference_match_columns, parser)

    classes_to_run = [args.mhc_class] if args.mhc_class else ['1', '2']

    for class_type in classes_to_run:
        if class_type == '1':
            prefix = "MHC_Class_I"
        elif class_type == '2':
            prefix = "MHC_Class_II"
        run_comparison(prefix, args.results_folder1, args.results_folder2, args.output_file, args.aggregated_columns, args.unaggregated_columns, args.reference_match_columns)



if __name__ == '__main__':
    main()