from scripts.run_utils import *



class CompareAggregatedTSV():
    def __init__(self, input_file1, input_file2, output_file, columns_to_compare):
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.output_path = output_file
        self.df1, self.df2 = load_tsv_files(self.input_file1, self.input_file2)
        self.contains_id = True
        self.replaced_id = False
        self.ID_replacement_cols = ['Gene', 'AA Change']
        self.columns_dropped_message = ""
        self.columns_to_compare = columns_to_compare
        self.common_variants = set()
        self.unique_variants_file1 = set()
        self.unique_variants_file2 = set()
        self.differences = {}



    def get_total_number_variants(self):
        """
        Purpose:    Get the total number of variants between the two files
        Modifies:   Nothing
        Returns:    Integer of the total number of variants
        """
        total_variants = len(self.common_variants)+len(self.unique_variants_file1)+len(self.unique_variants_file2)
        return total_variants



    def get_number_column_differences(self):
        """
        Purpose:    Get the number of differences for each column
        Modifies:   Nothing
        Returns:    Dictionary of the columns and corresponding differences
        """
        num_col_differences = {}
        for col, differences in self.differences.items():
            if (col != "ID"):
                num_col_differences[col] = len(differences)
        return num_col_differences



    def generate_differences_summary(self):
        """
        Purpose:    Create a summary of different statistics
        Modifies:   Nothing
        Returns:    String of the summary
        """
        total_vars = self.get_total_number_variants()
        common_vars = len(self.common_variants)
        num_unique_vars_file1 = len(self.unique_variants_file1)
        num_unique_vars_file2 = len(self.unique_variants_file2)
        summary = f"\n/* Differences Summary */\n"
        summary += f"-----------------------------\n"
        summary += f"Total number of variants: {total_vars}\n"
        summary += f"Number of common variants: {common_vars}\n"
        summary += f"Number of variants unique to file 1: {num_unique_vars_file1}\n"
        summary += f"Number of variants unique to file 2: {num_unique_vars_file2}\n"
        num_col_differences = self.get_number_column_differences()
        for col, _ in self.differences.items():
            if col != "ID":
                summary += f"-----\n"
                summary += f"Number of differences in {col}: {num_col_differences[col]}\n"
        return summary



    def generate_comparison_report(self):
        """
        Purpose:    Write all of the aggregated tsv differences found to the generated report
        Modifies:   Nothing
        Returns:    None
        """
        self.differences, self.unique_variants = get_file_differences(self.df1, self.df2, self.columns_to_compare, self.unique_variants_file1, self.unique_variants_file2, self.contains_id)
        
        if self.differences or self.unique_variants:
            first_unique_variant1 = True
            first_unique_variant2 = True
            try:
                with open(self.output_path, 'a') as f:
                    f.write("\n\n============================== AGGREGATED TSV COMPARISON ==============================\n\n\n")
                    f.write(f"File 1: {self.input_file1}\n")
                    f.write(f"File 2: {self.input_file2}\n")
                    if self.columns_dropped_message != "":
                        f.write(f"\n{self.columns_dropped_message}")
                    differences_summary = self.generate_differences_summary()
                    f.write(differences_summary)
                    if self.replaced_id:
                        f.write("\n\nID Format: 'Gene (AA_Change)'")
                                
                    for col, diffs in self.differences.items():
                        f.write(f"\n\n============[ DIFFERENCES IN {col.upper()} ]============\n\n\n")
                        f.write("ID\tFile 1\tFile 2\n")
                        for diff in diffs:
                            file1_value = diff.get(f'{col}_file1', 'NOT FOUND')
                            file2_value = diff.get(f'{col}_file2', 'NOT FOUND')
                            f.write(f"{diff['ID']}:\t{file1_value}\t->\t{file2_value}\n")

                    if self.unique_variants:
                        f.write(f"\n\n============[ UNIQUE VARIANTS ]============\n\n\n")
                        for diff in self.unique_variants:
                            if diff['File 2'] == '':
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
            print("The Aggregated TSV files are identical.")



    def check_columns(self):
        """
        Purpose:    Replace ID with Gene-AA_change if needed, output comparisons that have been dropped
        Modifies:   self.contains_id, self.columns_dropped_message
        Returns:    List of columns to keep in the comparison
        """
        df1_dropped_cols, df2_dropped_cols = drop_useless_columns(self.df1, self.df2, self.columns_to_compare)
        columns_to_keep = check_columns_to_compare(self.df1, self.df2, self.columns_to_compare)
        for col in df1_dropped_cols:
            if col == 'ID':
                self.contains_id = False
            else:
                if col in df2_dropped_cols:
                    print(u'\u2022', f"Comparison dropped: '{col}' is not present in either file")
                    self.columns_dropped_message += f"Comparison dropped: '{col}' is not present in either file\n"
                else:
                    print(u'\u2022', f"Comparison dropped: '{col}' is only present in file 1")
                    self.columns_dropped_message += f"Comparison dropped: '{col}' is only present in file 1\n"
        for col in df2_dropped_cols:
            if col not in df1_dropped_cols:
                if col == 'ID':
                    self.contains_id = False
                else:
                    print(u'\u2022', f"Comparison dropped: '{col}' is only present in file 2")
                    self.columns_dropped_message += f"Comparison dropped: '{col}' is only present in file 2\n"

        if not self.contains_id:
            can_replace = True
            for col in self.ID_replacement_cols:
                if col not in self.df1.columns or col not in self.df2.columns:
                    can_replace = False
            if can_replace:
                print(u'\u2022', "Replacing ID with Gene and AA Change")
                self.combine_gene_and_AA_change()
                self.replaced_id = True
        return columns_to_keep



    def combine_gene_and_AA_change(self):
        """
        Purpose:    Combines Gene and AA_Change into a singular unique ID column in both dataframes
        Modifies:   df1 and df2
        Returns:    None
        """
        self.df1['ID'] = self.df1[self.ID_replacement_cols[0]].astype(str) + ' (' + self.df1[self.ID_replacement_cols[1]].astype(str) + ')'
        self.df2['ID'] = self.df2[self.ID_replacement_cols[0]].astype(str) + ' (' + self.df2[self.ID_replacement_cols[1]].astype(str) + ')'

        self.df1.drop(columns=self.ID_replacement_cols, inplace=True)
        self.df2.drop(columns=self.ID_replacement_cols, inplace=True)