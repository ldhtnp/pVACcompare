from compare_tools import *
import argparse
import logging

logging.basicConfig(level=logging.DEBUG, format='%(message)s')

# TODO: Speed up identical file comparison
# TODO: Implement tests

def define_parser():
    """
    Purpose:    Define arguments for the parser that the user can use
    Modifies:   Nothing
    Returns:    The parser
    """
    valid_aggregated_columns = [
        "Gene",
        "AA Change",
        "Num Passing Transcripts",
        "Best Peptide",
        "Best Transcript",
        "Num Passing Peptides",
        "IC50 MT",
        "IC50 WT",
        "%%ile MT",
        "%%ile WT",
        "RNA Expr",
        "RNA VAF",
        "DNA VAF",
        "Tier",
    ]
    valid_unaggregated_columns = [
        "Biotype",
        "Sub-peptide Position",
        "Median MT IC50 Score",
        "Median WT IC50 Score",
        "Median MT Percentile",
        "Median WT Percentile",
        "WT Epitope Seq",
        "Tumor DNA VAF",
        "Tumor RNA Depth",
        "Tumor RNA VAF",
        "Gene Expression",
        "BigMHC_EL WT Score",
        "BigMHC_EL MT Score",
        "BigMHC_IM WT Score",
        "BigMHC_IM MT Score",
        "MHCflurryEL Processing WT Score",
        "MHCflurryEL Processing MT Score",
        "MHCflurryEL Presentation WT Score",
        "MHCflurryEL Presentation MT Score",
        "MHCflurryEL Presentation WT Percentile",
        "MHCflurryEL Presentation MT Percentile",
        "MHCflurry WT IC50 Score",
        "MHCflurry MT IC50 Score",
        "MHCflurry WT Percentile",
        "MHCflurry MT Percentile",
        "MHCnuggetsI WT IC50 Score",
        "MHCnuggetsI MT IC50 Score",
        "MHCnuggetsI WT Percentile",
        "MHCnuggetsI MT Percentile",
        "NetMHC WT IC50 Score",
        "NetMHC MT IC50 Score",
        "NetMHC WT Percentile",
        "NetMHC MT Percentile",
        "NetMHCcons WT IC50 Score",
        "NetMHCcons MT IC50 Score",
        "NetMHCcons WT Percentile",
        "NetMHCcons MT Percentile",
        "NetMHCpan WT IC50 Score",
        "NetMHCpan MT IC50 Score",
        "NetMHCpan WT Percentile",
        "NetMHCpan MT Percentile",
        "NetMHCpanEL WT Score",
        "NetMHCpanEL MT Score",
        "NetMHCpanEL WT Percentile",
        "NetMHCpanEL MT Percentile",
        "PickPocket WT IC50 Score",
        "PickPocket MT IC50 Score",
        "PickPocket WT Percentile",
        "PickPocket MT Percentile",
        "SMM WT IC50 Score",
        "SMM MT IC50 Score",
        "SMM WT Percentile",
        "SMM MT Percentile",
        "SMMPMBEC WT IC50 Score",
        "SMMPMBEC MT IC50 Score",
        "SMMPMBEC WT Percentile",
        "SMMPMBEC MT Percentile",
        "DeepImmuno WT Score",
        "DeepImmuno MT Score",
        "Problematic Positions",
    ]
    valid_reference_match_columns = [
        "Peptide",
        "Hit Definition",
        "Match Window",
        "Match Sequence",
    ]

    default_aggregated_columns = [
        "Num Passing Transcripts",
        "Best Peptide",
        "Best Transcript",
        "Num Passing Peptides",
        "Tier",
    ]
    default_unaggregated_columns = [
        "Biotype",
        "Sub-peptide Position",
        "Median MT IC50 Score",
        "Median WT IC50 Score",
        "Median MT Percentile",
        "Median WT Percentile",
        "WT Epitope Seq",
        "Tumor DNA VAF",
        "Tumor RNA Depth",
        "Tumor RNA VAF",
        "Gene Expression",
    ]
    default_reference_match_columns = ["Peptide", "Match Window"]

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("results_folder1", help="Path to first results input folder")
    parser.add_argument("results_folder2", help="Path to second results input folder")
    parser.add_argument("output_file", help="Name for generated report")
    parser.add_argument(
        "--mhc_class", choices=["1", "2"], help="Specify MHC class 1 or class 2"
    )
    parser.add_argument(
        "--aggregated_columns",
        type=lambda s: [a for a in s.split(",")],
        default=default_aggregated_columns,
        help=f"Comma-separated columns to include in the aggregated TSV comparison, choices: {', '.join(valid_aggregated_columns)}",
    )
    parser.add_argument(
        "--unaggregated_columns",
        type=lambda s: [a for a in s.split(",")],
        default=default_unaggregated_columns,
        help=f"Comma-separated columns to include in the unaggregated TSV comparison, choices: {', '.join(valid_unaggregated_columns)}",
    )
    parser.add_argument(
        "--reference_match_columns",
        type=lambda s: [a for a in s.split(",")],
        default=default_reference_match_columns,
        help=f"Comma-separated columns to include in the reference match TSV comparison, choices: {', '.join(valid_reference_match_columns)}",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--immuno_release",
        action="store_true",
        help="Use this flag if you are comparing results from immuno releases.",
    )
    group.add_argument(
        "--pvactools_release",
        action="store_true",
        help="Use this flag if you are comparing results from pvactools releases.",
    )

    return parser


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

    classes_to_run = [args.mhc_class] if args.mhc_class else ["1", "2"]

    for class_type in classes_to_run:
        if args.pvactools_release:
            if class_type == "1":
                prefix = "MHC_Class_I"
            elif class_type == "2":
                prefix = "MHC_Class_II"
        else:
            if class_type == "1":
                prefix = "pVACseq/mhc_i"
            elif class_type == "2":
                prefix = "pVACseq/mhc_ii"
        run_comparison(
            prefix,
            args.results_folder1,
            args.results_folder2,
            args.output_file,
            args.aggregated_columns,
            args.unaggregated_columns,
            args.reference_match_columns,
        )


if __name__ == "__main__":
    main()
