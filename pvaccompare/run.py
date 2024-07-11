import argparse
import glob
import os
from scripts import run_compare_aggregated_tsv
from scripts import run_compare_unaggregated_tsv
from scripts import run_compare_yml
from scripts import run_compare_json


def define_parser():
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
    valid_columns = ["Gene", "AA Change", "Num Passing Transcripts", "Best Peptide", "Best Transcript", "Num Passing Peptides", "IC50 MT", "IC50 WT", "%ile MT", "%ile WT", "RNA Expr", "RNA VAF", "DNA VAF", "Tier"]
    for col in columns_to_compare:
        if col not in valid_columns:
            parser.error(f"Invalid column '{col}' specified.\nValid columns are: {', '.join(valid_columns)}")


def find_file(results_folder, subfolder, pattern):
    search_path = os.path.join(results_folder, subfolder, pattern)
    files = glob.glob(search_path, recursive=True)
    return files[0] if files else None


def main():
    parser = define_parser()
    args = parser.parse_args()

    validate_columns(args.columns_to_compare, parser)

    classes_to_run = [args.mhc_class] if args.mhc_class else ['1', '2']

    for class_type in classes_to_run:
        if class_type == '1':
            output_file = args.output_file + "_MHC_Class_I.tsv"

            yml1_path = find_file(args.results_folder1, "MHC_Class_I/log", 'inputs.yml')
            yml2_path = find_file(args.results_folder2, "MHC_Class_I/log", 'inputs.yml')
            if yml1_path and yml2_path:
                run_compare_yml.main(yml1_path, yml2_path, output_file)
            else:
                if yml1_path:
                    print("Could not locate the input YML file in results folder 1 for MHC Class I.")
                else:
                    print("Could not locate the input YML file in results folder 2 for MHC Class I.")

            agg_tsv1_path = find_file(args.results_folder1, "MHC_Class_I/", '*all_epitopes.aggregated.tsv')
            agg_tsv2_path = find_file(args.results_folder2, "MHC_Class_I/", '*all_epitopes.aggregated.tsv')
            if agg_tsv1_path and agg_tsv2_path:
                run_compare_aggregated_tsv.main(agg_tsv1_path, agg_tsv2_path, output_file, args.columns_to_compare)
            else:
                if yml1_path:
                    print("Could not locate the aggregated TSV file in results folder 1 for MHC Class I.")
                else:
                    print("Could not locate the aggregated TSV file in results folder 2 for MHC Class I.")

            json1_path = find_file(args.results_folder1, "MHC_Class_I/", '*all_epitopes.aggregated.metrics.json')
            json2_path = find_file(args.results_folder2, "MHC_Class_I/", '*all_epitopes.aggregated.metrics.json')
            if json1_path and json2_path:
                run_compare_json.main(json1_path, json2_path, output_file)
            else:
                if yml1_path:
                    print("Could not locate the metrics JSON file in results folder 1 for MHC Class I.")
                else:
                    print("Could not locate the metrics JSON file in results folder 2 for MHC Class I.")
            
            unagg_tsv1_path = find_file(args.results_folder1, "MHC_Class_I/", '*all_epitopes.tsv')
            unagg_tsv2_path = find_file(args.results_folder2, "MHC_Class_I/", '*all_epitopes.tsv')
            if unagg_tsv1_path and unagg_tsv2_path:
                run_compare_unaggregated_tsv.main(unagg_tsv1_path, unagg_tsv2_path, output_file)
            else:
                if yml1_path:
                    print("Could not locate the unaggregated TSV file in results folder 1 for MHC Class I.")
                else:
                    print("Could not locate the unaggregated TSV file in results folder 2 for MHC Class I.")
            print("Successfully generated MHC Class I comparison report.")
        elif class_type == '2':
            output_file = args.output_file + "_MHC_Class_II.tsv"

            yml1_path = find_file(args.results_folder1, "MHC_Class_II/log", 'inputs.yml')
            yml2_path = find_file(args.results_folder2, "MHC_Class_II/log", 'inputs.yml')
            if yml1_path and yml2_path:
                run_compare_yml.main(yml1_path, yml2_path, output_file)
            else:
                if yml1_path:
                    print("Could not locate the input YML file in results folder 1 for MHC Class II.")
                else:
                    print("Could not locate the input YML file in results folder 2 for MHC Class II.")

            tsv1_path = find_file(args.results_folder1, "MHC_Class_II/", '*all_epitopes.aggregated.tsv')
            tsv2_path = find_file(args.results_folder2, "MHC_Class_II/", '*all_epitopes.aggregated.tsv')
            if tsv1_path and tsv2_path:
                run_compare_aggregated_tsv.main(tsv1_path, tsv2_path, output_file, args.columns_to_compare)
            else:
                if yml1_path:
                    print("Could not locate the aggregated TSV file in results folder 1 for MHC Class II.")
                else:
                    print("Could not locate the aggregated TSV file in results folder 2 for MHC Class II.")

            json1_path = find_file(args.results_folder1, "MHC_Class_II/", '*all_epitopes.aggregated.metrics.json')
            json2_path = find_file(args.results_folder2, "MHC_Class_II/", '*all_epitopes.aggregated.metrics.json')
            if json1_path and json2_path:
                run_compare_json.main(json1_path, json2_path, output_file)
            else:
                if yml1_path:
                    print("Could not locate the metrics JSON file in results folder 1 for MHC Class II.")
                else:
                    print("Could not locate the metrics JSON file in results folder 2 for MHC Class II.")
            
            unagg_tsv1_path = find_file(args.results_folder1, "MHC_Class_II/", '*all_epitopes.tsv')
            unagg_tsv2_path = find_file(args.results_folder2, "MHC_Class_II/", '*all_epitopes.tsv')
            if unagg_tsv1_path and unagg_tsv2_path:
                run_compare_unaggregated_tsv.main(unagg_tsv1_path, unagg_tsv2_path, output_file)
            else:
                if yml1_path:
                    print("Could not locate the unaggregated TSV file in results folder 1 for MHC Class II.")
                else:
                    print("Could not locate the unaggregated TSV file in results folder 2 for MHC Class II.")
            print("Successfully generated MHC Class II comparison report.")


if __name__ == '__main__':
    main()