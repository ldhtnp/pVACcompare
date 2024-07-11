import pandas as pd
import numpy as np
import re
#from scripts.compare_unaggregated_tsv import CompareUnaggregatedTSV


class CompareUnaggregatedTSV():
    def __init__(self, run_utils, input_file1, input_file2):
        self.run_utils = run_utils
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.output_path = run_utils.output_path
        self.df1, self.df2 = run_utils.load_tsv_files(self.input_file1, self.input_file2)
        self.ID_columns = ['Chromosome', 'Start', 'Stop', 'Reference', 'Variant']
        self.columns_to_compare = ['Transcript', 'Transcript Support Level', 'Ensembl Gene ID', 'Variant Type', 'Mutation', 'Gene Name', 'Peptide Length']
        self.common_variants = set()
        self.unique_variants_file1 = set()
        self.unique_variants_file2 = set()
        self.differences = {}
    

    def create_ID_column(self):
        self.df1['ID'] = self.df1[self.ID_columns].apply(lambda x: '-'.join(map(str, x)), axis=1)
        self.df2['ID'] = self.df2[self.ID_columns].apply(lambda x: '-'.join(map(str, x)), axis=1)

        self.df1.drop(columns=self.ID_columns, inplace=True)
        self.df2.drop(columns=self.ID_columns, inplace=True)

    
    def drop_unique_columns(self):
        cols1_to_drop = []
        cols2_to_drop = []
        for col in self.df1.columns:
            if col not in self.df2.columns:
                cols1_to_drop.append(col)
        for col in self.df2.columns:
            if col not in self.df1.columns:
                cols2_to_drop.append(col)
        self.df1.drop(columns=cols1_to_drop, inplace=True)
        self.df2.drop(columns=cols2_to_drop, inplace=True)
    

    def drop_additional_columns(self):
        cols1_to_drop = [col for col in self.df1.columns if (col not in self.columns_to_compare) and (col != 'ID')]
        cols2_to_drop = [col for col in self.df2.columns if (col not in self.columns_to_compare) and (col != 'ID')]

        if cols1_to_drop:
            self.df1.drop(columns=cols1_to_drop, inplace=True)

        if cols2_to_drop:
            self.df2.drop(columns=cols2_to_drop, inplace=True)
    

    def generate_comparison_report(self):
        self.differences = self.run_utils.get_file_differences(self.df1, self.df2, self.unique_variants_file1, self.unique_variants_file2, self.columns_to_compare)
        
        if self.differences:
            first_unique_variant1 = True
            first_unique_variant2 = True
            try:
                with open(self.output_path, 'a') as f:
                    f.write("\n============================== UNAGGREGATED TSV COMPARISON ==============================\n\n\n")
                    f.write(f"File 1: {self.input_file1}\n")
                    f.write(f"File 2: {self.input_file2}\n")
                    if self.columns_dropped_message != "":
                        f.write(f"\n{self.columns_dropped_message}")
                    differences_summary = self.generate_differences_summary()
                    f.write(differences_summary)
                    if self.replaced_ID:
                        f.write("\n\nID Format: 'Gene (AA_Change)'")
                    for col, diffs in self.differences.items():
                        if col == "ID":
                            f.write(f"\n\n============[ UNIQUE VARIANTS ]============\n\n\n")
                            for diff in diffs:
                                if (diff['File 2'] == ''):
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
                        else:
                            f.write(f"\n\n============[ DIFFERENCES IN {col.upper()} ]============\n\n\n")
                            f.write("ID\tFile 1\tFile 2\n")
                            for diff in diffs:
                                f.write(f"{diff['ID']}:\t{diff['File 1']}\t->\t{diff['File 2']}\n")
            except Exception as e:
                raise Exception(f"Error writing differences to file: {e}")
        else:
            print("The files are identical.")


def main(run_utils, input_file1, input_file2):
    comparer = CompareUnaggregatedTSV(run_utils, input_file1, input_file2)

    comparer.create_ID_column()
    comparer.common_variants = run_utils.get_common_variants(comparer.df1, comparer.df2)
    comparer.unique_variants_file1, comparer.unique_variants_file2 = comparer.run_utils.get_unique_variants(comparer.df2, comparer.df2, comparer.common_variants)

    comparer.drop_unique_columns()
    comparer.drop_additional_columns()
    
    if comparer.df1.shape != comparer.df2.shape:
        comparer.df1, comparer.df2 = run_utils.make_rows_equal(comparer.df1, comparer.df2)
    comparer.generate_comparison_report()


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])