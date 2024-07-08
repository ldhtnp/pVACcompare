import argparse
import sys
import glob
import os
from scripts.run_utils import RunUtils
from scripts import run_compare_tsv
from scripts import run_compare_yml
from scripts import run_compare_json

def define_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('results_folder1', help="Path to first results input folder")
    parser.add_argument('results_folder2', help="Path to second results input folder")
    parser.add_argument('output_file', help="Name for generated report")
    parser.add_argument('--mhc_class', choices=['1', '2'], help="Specify MHC class 1 or class 2")
    return parser

def find_file(results_folder, subfolder, pattern):
    search_path = os.path.join(results_folder, subfolder, pattern)
    files = glob.glob(search_path, recursive=True)
    return files[0] if files else None

def main():
    parser = define_parser()
    args = parser.parse_args()

    classes_to_run = [args.mhc_class] if args.mhc_class else ['1', '2']

    for class_type in classes_to_run:
        if class_type == '1':
            output_file = args.output_file + "_MHC_Class_I.tsv"
            run_utils = RunUtils(output_file)
            yml1_path = find_file(args.results_folder1, "MHC_Class_I/log", 'inputs.yml')
            yml2_path = find_file(args.results_folder2, "MHC_Class_I/log", 'inputs.yml')
            if yml1_path and yml2_path:
                run_compare_yml.main(run_utils, yml1_path, yml2_path)
            else:
                raise Exception("Could not locate the YML input files for MHC Class I.")

            tsv1_path = find_file(args.results_folder1, "MHC_Class_I/", '*all_epitopes.aggregated.tsv')
            tsv2_path = find_file(args.results_folder2, "MHC_Class_I/", '*all_epitopes.aggregated.tsv')
            if tsv1_path and tsv2_path:
                run_compare_tsv.main(run_utils, tsv1_path, tsv2_path)
            else:
                raise Exception("Could not locate the aggregated TSV files for MHC Class I.")

            # json1_path = find_file(args.results_folder1, "MHC_Class_I/", '*all_epitopes.aggregated.metrics.json')
            # json2_path = find_file(args.results_folder2, "MHC_Class_I/", '*all_epitopes.aggregated.metrics.json')
            # if json1_path and json2_path:
            #     run_compare_json.main(run_utils, json1_path, json2_path)
            # else:
            #     raise Exception("Could not locate the JSON metric files for MHC Class I.")
        elif class_type == '2':
            output_file = args.output_file + "_MHC_Class_II.tsv"
            run_utils = RunUtils(output_file)
            yml1_path = find_file(args.results_folder1, "MHC_Class_II/log", 'inputs.yml')
            yml2_path = find_file(args.results_folder2, "MHC_Class_II/log", 'inputs.yml')
            if yml1_path and yml2_path:
                run_compare_yml.main(run_utils, yml1_path, yml2_path)
            else:
                raise Exception("Could not locate the YML input files for MHC Class II.")

            tsv1_path = find_file(args.results_folder1, "MHC_Class_II/", '*all_epitopes.aggregated.tsv')
            tsv2_path = find_file(args.results_folder2, "MHC_Class_II/", '*all_epitopes.aggregated.tsv')
            if tsv1_path and tsv2_path:
                run_compare_tsv.main(run_utils, tsv1_path, tsv2_path)
            else:
                raise Exception("Could not locate the aggregated TSV files for MHC Class II.")

            # json1_path = find_file(args.results_folder1, "MHC_Class_II/", '*all_epitopes.aggregated.metrics.json')
            # json2_path = find_file(args.results_folder2, "MHC_Class_II/", '*all_epitopes.aggregated.metrics.json')
            # if json1_path and json2_path:
            #     run_compare_json.main(run_utils, json1_path, json2_path)
            # else:
            #     raise Exception("Could not locate the JSON metric files for MHC Class II.")

if __name__ == '__main__':
    main()
