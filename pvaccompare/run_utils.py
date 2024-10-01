import pandas as pd
import numpy as np
import re
import logging


def check_column_formatting(df1, df2):
    """
    Purpose:    Rename columns based on the mappings dictionary to make column names the same
    Modifies:   df1 and df2
    Returns:    None
    """
    column_mappings = {  # Fill in different names/formatting between versions
        "Best Peptide": ["best peptide", "best_peptide"],
        "Best Transcript": ["best transcript", "best_transcript"],
        "Tier": ["tier"],
        "AA Change": ["AA_change"],
        "Num Passing Transcripts": ["Num_Transcript"],
        "Num Passing Peptides": ["Num_Peptides"],
    }

    for col in df1.columns:
        for key, value in column_mappings.items():
            if col == key:
                break
            elif col in value:
                logging.info("\u2022 Renamed '%s' to '%s' in file 1", col, key)
                df1.rename(columns={col: key}, inplace=True)
                break
    for col in df2.columns:
        for key, value in column_mappings.items():
            if col == key:
                break
            elif col in value:
                logging.info("\u2022 Renamed '%s' to '%s' in file 2", col, key)
                df2.rename(columns={col: key}, inplace=True)
                break


def output_dropped_cols(cols1_to_drop, cols2_to_drop):
    """
    Purpose:    Outputs the dropped comparison columns to the terminal and creates a columns dropped message for the generated report
    Modifies:   Nothing
    Returns:    String columns_dropped_message
    """
    columns_dropped_message = ""
    for col in cols1_to_drop:
        if col in cols2_to_drop:
            logging.info(
                "\u2022 Comparison dropped: '%s' is not present in either file", col
            )
            columns_dropped_message += (
                f"Comparison dropped: '{col}' is not present in either file\n"
            )
        else:
            logging.info(
                "\u2022 Comparison dropped: '%s' is only present in file 1", col
            )
            columns_dropped_message += (
                f"Comparison dropped: '{col}' is only present in file 1\n"
            )
    for col in cols2_to_drop:
        if col not in cols1_to_drop:
            logging.info(
                "\u2022 Comparison dropped: '%s' is only present in file 2", col
            )
            columns_dropped_message += (
                f"Comparison dropped: '{col}' is only present in file 2\n"
            )
    return columns_dropped_message


def get_common_variants(df1, df2):
    """
    Purpose:    Find and store IDs shared between the two given dataframes
    Modifies:   Nothing
    Returns:    A set containing IDs that are common between the two dataframes
    """
    return set(df1["ID"]).intersection(set(df2["ID"]))


def load_tsv_files(input_file1, input_file2):
    """
    Purpose:    Load the two input tsv files into dataframes
    Modifies:   Nothing
    Returns:    Two dataframes corresponding to the two input files
    """
    try:
        df1 = pd.read_csv(input_file1, sep="\t", low_memory=False)
        df2 = pd.read_csv(input_file2, sep="\t", low_memory=False)
    except Exception as e:
        raise Exception(f"Error loading files: {e}")
    return df1, df2


def make_rows_equal(df1, df2):
    """
    Purpose:    Add 'dummy data' to make the two dataframes have an equal number of rows
    Modifies:   One of the two dataframes depending on which is smaller
    Returns:    Two dataframes
    """
    num_rows_to_add = abs(df1.shape[0] - df2.shape[0])
    if df1.shape[0] > df2.shape[0]:
        dummy_data = pd.DataFrame(
            np.nan, index=range(num_rows_to_add), columns=df2.columns
        )
        df2 = pd.concat([df2, dummy_data], ignore_index=True)
    else:
        dummy_data = pd.DataFrame(
            np.nan, index=range(num_rows_to_add), columns=df1.columns
        )
        df1 = pd.concat([df1, dummy_data], ignore_index=True)
    return df1, df2


def drop_useless_columns(df1, df2, columns_to_compare):
    """
    Purpose:    First removes columns that are not included in the comparison, excluding 'ID', then removes columns not present
                in both files
    Modifies:   df1 and df2
    Returns:    Two lists containing the columns dropped in the corresponding dataframes
    """
    columns_to_keep = set(["ID"])
    if "ID" not in df1.columns or "ID" not in df2.columns:
        columns_to_keep.update(["Gene", "AA Change"])

    # Drop columns that are not in columns_to_compare and not 'ID'
    cols1_to_drop = [
        col
        for col in df1.columns
        if (col not in columns_to_compare) and (col not in columns_to_keep)
    ]
    cols2_to_drop = [
        col
        for col in df2.columns
        if (col not in columns_to_compare) and (col not in columns_to_keep)
    ]

    df1.drop(columns=cols1_to_drop, inplace=True)
    df2.drop(columns=cols2_to_drop, inplace=True)

    # Drop columns that are not present in both dataframes
    common_cols = set(df1.columns).intersection(set(df2.columns))
    cols1_to_drop = [col for col in df1.columns if col not in common_cols]
    cols2_to_drop = [col for col in df2.columns if col not in common_cols]

    df1.drop(columns=cols1_to_drop, inplace=True)
    df2.drop(columns=cols2_to_drop, inplace=True)

    return cols1_to_drop, cols2_to_drop


def check_columns_to_compare(df1, df2, columns_to_compare):
    """
    Purpose:    Add columns present in both dataframes to columns_to_keep
    Modifies:   Nothing
    Returns:    List of columns present in both dataframes
    """
    columns_to_keep = []
    for col in columns_to_compare:
        if col in df1.columns and col in df2.columns:
            columns_to_keep.append(col)
    return columns_to_keep


def get_unique_variants(df1, df2, common_variants):
    """
    Purpose:    Find and store unique variants to each dataframe
    Modifies:   Nothing
    Returns:    Two sets containing IDs unique to the corresponding dataframes
    """
    unique_variants_file1 = set(df1["ID"]).difference(common_variants)
    unique_variants_file2 = set(df2["ID"]).difference(common_variants)
    return unique_variants_file1, unique_variants_file2


def extract_id_parts(id_str):
    """
    Purpose:    Extract parts of the ID to use in sorting
    Modifies:   Nothing
    Returns:    A tuple of the different sections for sorting
    """
    match = re.match(r"chr(\w+)-(\d+)-(\d+)-", id_str)
    if match:
        chr_part = match.group(1)
        if chr_part.isdigit():
            chr_part = int(chr_part)
        else:
            chr_part = float("inf")
        return chr_part, int(match.group(2)), int(match.group(3))
    return None, None, None


def split_replaced_id(id_str):
    """
    Purpose:    Extract parts of the replaced ID (Gene-AA change) to use in sorting
    Modifies:   Nothing
    Returns:    Two strings corresponding to the split sections
    """
    try:
        grp1, rest = id_str.split(" (")
        grp2 = rest.split("-")[0].rstrip(")")
        return grp1, grp2
    except Exception as e:
        logging.error(f"Error splitting replaced ID: {id_str}, {e}")
        return "", ""


def get_file_differences(
    df1,
    df2,
    columns_to_compare,
    unique_variants_file1,
    unique_variants_file2,
    contains_id=True,
    tolerance=0.1,
):
    """
    Purpose:    Find and store differences found between the two dataframes
    Modifies:   Nothing
    Returns:    Dictionary of differences and a dictionary of unique variants
    """
    merged_df = pd.merge(df1, df2, on="ID", suffixes=("_file1", "_file2"))

    differences = {}
    for col in columns_to_compare:
        col_file1 = f"{col}_file1"
        col_file2 = f"{col}_file2"

        # Convert columns to numeric
        merged_df[col_file1] = pd.to_numeric(merged_df[col_file1], errors="coerce")
        merged_df[col_file2] = pd.to_numeric(merged_df[col_file2], errors="coerce")

        # Determine if columns are numeric
        is_numeric_col1 = np.issubdtype(merged_df[col_file1].dtype, np.number)
        is_numeric_col2 = np.issubdtype(merged_df[col_file2].dtype, np.number)

        mask = (merged_df[col_file1].notna() | merged_df[col_file2].notna()) & (
            merged_df[col_file1] != merged_df[col_file2]
        )
        if is_numeric_col1 and is_numeric_col2:
            tolerance_mask = (
                np.abs(merged_df[col_file1] - merged_df[col_file2]) > tolerance
            )
            mask = mask & tolerance_mask

        diff = merged_df[mask][["ID", col_file1, col_file2]]
        if not diff.empty:
            differences[col] = diff.to_dict("records")

    for col in differences:
        if contains_id:
            differences[col] = sorted(
                differences[col], key=lambda x: extract_id_parts(x["ID"])
            )
        else:
            differences[col] = sorted(
                differences[col], key=lambda x: split_replaced_id(x["ID"])
            )

    unique_variants = []
    # Include unique variants
    if unique_variants_file1 or unique_variants_file2:
        for variant in unique_variants_file1:
            unique_variants.append({"File 1": variant, "File 2": ""})
        for variant in unique_variants_file2:
            unique_variants.append({"File 1": "", "File 2": variant})

    # Sort unique variants
    if contains_id:
        unique_variants = sorted(
            unique_variants,
            key=lambda x: extract_id_parts(x["File 1"] if x["File 1"] else x["File 2"]),
        )
    else:
        unique_variants = sorted(
            unique_variants,
            key=lambda x: split_replaced_id(
                x["File 1"] if x["File 1"] else x["File 2"]
            ),
        )

    return differences, unique_variants


def get_total_number_variants(
    common_variants, unique_variants_file1, unique_variants_file2
):
    """
    Purpose:    Get the total number of variants between the two files
    Modifies:   Nothing
    Returns:    Integer of the total number of variants
    """
    total_variants = (
        len(common_variants) + len(unique_variants_file1) + len(unique_variants_file2)
    )
    return total_variants


def get_number_column_differences(differences):
    """
    Purpose:    Get the number of differences for each column
    Modifies:   Nothing
    Returns:    Dictionary of the columns and corresponding differences
    """
    num_col_differences = {}
    for col, differences in differences.items():
        if col != "ID":
            num_col_differences[col] = len(differences)
    return num_col_differences


def generate_differences_summary(
    common_variants, unique_variants_file1, unique_variants_file2, differences={}
):
    """
    Purpose:    Create a summary of different statistics
    Modifies:   Nothing
    Returns:    String of the summary
    """
    total_vars = get_total_number_variants(
        common_variants, unique_variants_file1, unique_variants_file2
    )
    common_vars = len(common_variants)
    num_unique_vars_file1 = len(unique_variants_file1)
    num_unique_vars_file2 = len(unique_variants_file2)
    summary = f"\n/* Differences Summary */\n"
    summary += f"-----------------------------\n"
    summary += f"Total number of variants: {total_vars}\n"
    summary += f"Number of common variants: {common_vars}\n"
    summary += f"Number of variants unique to file 1: {num_unique_vars_file1}\n"
    summary += f"Number of variants unique to file 2: {num_unique_vars_file2}\n"
    num_col_differences = get_number_column_differences(differences)
    for col, _ in differences.items():
        if col != "ID":
            summary += f"-----\n"
            summary += f"Number of differences in {col}: {num_col_differences[col]}\n"
    return summary


def generate_comparison_report(
    tool,
    id_format,
    differences,
    unique_variants,
    input_file1,
    input_file2,
    output_path,
    columns_dropped_message="",
    differences_summary="",
    replaced_id=False,
):
    """
    Purpose:    Handles writing the aggregated and unaggregated tsv differences to the generated report
    Modifies:   Nothing
    Returns:    None
    """
    if differences or unique_variants:
        first_unique_variant1 = True
        first_unique_variant2 = True
        try:
            with open(output_path, "a") as f:
                f.write(
                    f"\n\n============================== {tool.upper()} COMPARISON ==============================\n\n\n"
                )
                f.write(f"File 1: {input_file1}\n")
                f.write(f"File 2: {input_file2}\n")
                if columns_dropped_message != "":
                    f.write(f"\n{columns_dropped_message}")
                if differences_summary != "":
                    f.write(differences_summary)

                for col, diffs in differences.items():
                    f.write(
                        f"\n\n============[ DIFFERENCES IN {col.upper()} ]============\n\n\n"
                    )
                    if replaced_id:
                        f.write("ID Format: 'Gene (AA_Change)'\n\n")
                    else:
                        f.write(f"ID Format: {id_format}\n\n")
                    f.write("ID\tFile 1\tFile 2\n")
                    for diff in diffs:
                        file1_value = diff.get(f"{col}_file1", "NOT FOUND")
                        file2_value = diff.get(f"{col}_file2", "NOT FOUND")
                        f.write(f"{diff['ID']}:\t{file1_value}\t->\t{file2_value}\n")

                if unique_variants:
                    f.write(f"\n\n============[ UNIQUE VARIANTS ]============\n\n\n")
                    if replaced_id:
                        f.write("Variant Format: 'Gene (AA_Change)'\n\n")
                    else:
                        f.write(f"Variant Format: {id_format}\n\n")
                    for diff in unique_variants:
                        if diff["File 2"] == "":
                            if first_unique_variant1:
                                f.write("Variants Unique to File 1:\n")
                                first_unique_variant1 = False
                            f.write(f"\t{diff['File 1']}\n")
                        else:
                            if first_unique_variant2:
                                if not first_unique_variant1:
                                    f.write("\n")
                                f.write("Variants Unique to File 2:\n")
                                first_unique_variant2 = False
                            f.write(f"\t{diff['File 2']}\n")
        except Exception as e:
            raise Exception(f"Error writing differences to file: {e}")
    else:
        logging.info("The %s files are identical.", tool)
