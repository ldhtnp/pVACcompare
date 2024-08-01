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



    def check_id(self, cols1_to_drop, cols2_to_drop):
        """
        Purpose:    Replace ID with Gene-AA_change if needed
        Modifies:   self.contains_id, self.replaced_id
        Returns:    None
        """
        if 'ID' in cols1_to_drop or 'ID' in cols2_to_drop:
            self.contains_id = False

        if not self.contains_id:
            can_replace = True
            for col in self.ID_replacement_cols:
                if col not in self.df1.columns or col not in self.df2.columns:
                    can_replace = False
            if can_replace:
                self.combine_gene_and_AA_change()
                print(u'\u2022', "Replaced ID with Gene and AA Change")
                self.replaced_id = True



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