from run_utils import *
import logging


class CompareReferenceMatchesTSV:
    def __init__(self, input_file1, input_file2, output_file, columns_to_compare):
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.output_path = output_file
        self.df1, self.df2 = load_tsv_files(self.input_file1, self.input_file2)
        self.columns_to_compare = columns_to_compare
        self.hits_file1 = {}
        self.hits_file2 = {}

    def create_id_column(self):
        """
        Purpose:    Combines multiple columns into a singular unique ID column in both dataframes
        Modifies:   df1 and df2
        Returns:    None
        """
        id_columns = [
            "Chromosome",
            "Start",
            "Stop",
            "Reference",
            "Variant",
            "Transcript",
            "MT Epitope Seq",
            "Hit ID",
            "Match Start",
            "Match Stop",
        ]
        self.df1["ID"] = self.df1[id_columns].apply(
            lambda x: "-".join(map(str, x)), axis=1
        )
        self.df2["ID"] = self.df2[id_columns].apply(
            lambda x: "-".join(map(str, x)), axis=1
        )

        self.df1.drop(columns=id_columns, inplace=True)
        self.df2.drop(columns=id_columns, inplace=True)

    def check_duplicate_ids(self):
        """
        Purpose:    Checks if duplicate IDs exist in either dataframe
        Modifies:   Nothing
        Returns:    Boolean value
        """
        self.hits_file1 = self.df1["ID"].value_counts().to_dict()
        self.hits_file2 = self.df2["ID"].value_counts().to_dict()

        max_hits_file1 = max(self.hits_file1.values(), default=0)
        max_hits_file2 = max(self.hits_file2.values(), default=0)

        if max_hits_file1 > 1 or max_hits_file2 > 1:
            if max_hits_file1 > 1 and max_hits_file2 > 1:
                logging.error(
                    "ERROR: Duplicate unique records were found in both files. Writing number of hits only."
                )
            elif max_hits_file1 > 1:
                logging.error(
                    "ERROR: Duplicate unique records were found in file 1. Writing number of hits only."
                )
            else:
                logging.error(
                    "ERROR: Duplicate unique records were found in file 2. Writing number of hits only."
                )
            return True
        else:
            return False

    def output_counts(self, differences_summary, id_format):
        """
        Purpose:    Write all of the unique variants and their number of hits to the generated report
        Modifies:   Nothing
        Returns:    None
        """
        sorted_hits_file1 = dict(
            sorted(self.hits_file1.items(), key=lambda x: extract_id_parts(x[0]))
        )
        sorted_hits_file2 = dict(
            sorted(self.hits_file2.items(), key=lambda x: extract_id_parts(x[0]))
        )

        with open(self.output_path, "a") as f:
            f.write(
                f"\n\n============================== REFERENCE MATCH TSV COMPARISON ==============================\n\n\n"
            )
            f.write(f"File 1: {self.input_file1}\n")
            f.write(f"File 2: {self.input_file2}\n")
            f.write(f"\n{differences_summary}")
            f.write(f"\n\n============[ UNIQUE VARIANTS ]============\n\n\n")
            f.write(f"Variant Format: {id_format}: Number of Hits\n")
            f.write("\nVariants Unique to File 1:\n")
            for key, value in sorted_hits_file1.items():
                f.write(f"\t{key}:\t{value}\n")

            f.write("\nVariants Unique to File 2:\n")
            for key, value in sorted_hits_file2.items():
                f.write(f"\t{key}:\t{value}\n")
