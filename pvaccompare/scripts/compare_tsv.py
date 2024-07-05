import pandas as pd
import numpy as np
import re
import datetime


class CompareTSV():
    def __init__(self, run_utils, input_file1, input_file2, output_path, columns_to_compare):
        self.run_utils = run_utils
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.output_path = output_path
        self.df1, self.df2 = self.load_tsv_files()
        self.run_utils.fill_common_rows(self.df1, self.df2)
        self.contains_ID = False
        self.replaced_ID = False
        self.ID_replacement_cols = ['Gene', 'AA Change']
        self.differences = {}
        self.column_mappings = { # Fill in different names/formatting between versions
            'Best Peptide': ['best peptide', 'best_peptide'],
            'Best Transcript': ['best transcript', 'best_transcript'],
            'Tier': ['tier'],
            'AA Change': ['AA_change'],
            'Num Passing Transcripts': ['Num_Transcript'],
            'Num Passing Peptides': ['Num_Peptides'],
        }
        self.columns_dropped_message = ""
        self.columns_to_compare = self.check_columns(columns_to_compare)
        self.unique_variants_file1, self.unique_variants_file2 = self.get_unique_variants() if self.contains_ID or self.replaced_ID else set()


    def load_tsv_files(self):
        try:
            df1 = pd.read_csv(self.input_file1, sep='\t')
            df2 = pd.read_csv(self.input_file2, sep='\t')
        except Exception as e:
            raise Exception(f"Error loading files: {e}")
        return df1, df2


    def compare_rows_with_ID(self, row_file1, row_file2):
        for col in self.columns_to_compare:
            value_file1 = row_file1[col].values[0]
            value_file2 = row_file2[col].values[0]
            if value_file1 != value_file2:
                if col not in self.differences:
                    self.differences[col] = []
                self.differences[col].append({
                    'ID': row_file1['ID'].values[0],
                    'File 1': value_file1,
                    'File 2': value_file2
                })


    def get_unique_variants(self):
        unique_variants_file1 = set()
        unique_variants_file2 = set()
        for value in self.df1['ID'].values:
            if value not in self.common_rows and not pd.isna(value):
                unique_variants_file1.add(value)
        
        for value in self.df2['ID'].values:
            if value not in self.common_rows and not pd.isna(value):
                unique_variants_file2.add(value)
        return unique_variants_file1, unique_variants_file2


    def get_file_differences(self):
        for value1 in self.df1['ID'].values:
            if value1 not in self.unique_variants_file1:
                for value2 in self.df2['ID'].values:
                    if value2 not in self.unique_variants_file2:
                        if (value1 == value2):
                            row_file1 = self.df1.loc[self.df1['ID'] == value1]
                            row_file2 = self.df2.loc[self.df2['ID'] == value2]
                            self.compare_rows_with_ID(row_file1, row_file2)

        if self.unique_variants_file1 or self.unique_variants_file2:
            if 'ID' not in self.differences:
                self.differences['ID'] = []
            for variant in self.unique_variants_file1:
                self.differences['ID'].append({
                        'File 1': variant,
                        'File 2': ''
                    })
            for variant in self.unique_variants_file2:
                self.differences['ID'].append({
                        'File 1': '',
                        'File 2': variant
                    })


    def get_total_number_variants(self):
        total_num_vars = len(self.common_rows)
        for value in self.unique_variants_file1:
            total_num_vars += 1
        for value in self.unique_variants_file2:
            total_num_vars += 1
        return total_num_vars


    def get_number_column_differences(self):
        num_col_differences = {}
        for col, differences in self.differences.items():
            if (col != "ID"):
                num_col_differences[col] = len(differences)
        return num_col_differences


    def generate_differences_summary(self):
        total_vars = self.get_total_number_variants()
        common_vars = len(self.common_rows)
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
        self.get_file_differences()
        
        if self.differences:
            first_unique_variant1 = True
            first_unique_variant2 = True
            try:
                with open(self.output_path, 'w') as f:
                    f.write(f"Report Generation Date and Time: {datetime.datetime.now()}\n\n")
                    f.write(f"File 1: {self.input_file1}\n")
                    f.write(f"File 2: {self.input_file2}\n")
                    if self.columns_dropped_message != "":
                        f.write(f"\n{self.columns_dropped_message}\n")
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
                print(f"Successfully generated comparison report.")
            except Exception as e:
                raise Exception(f"Error writing differences to file: {e}")
        else:
            print("The files are identical.")


    def check_column_formatting(self):
        for col in self.df1.columns:
            for key, value in self.column_mappings.items():
                if col == key:
                    break
                elif col in value:
                    self.df1.rename(columns={col: key}, inplace=True)
                    break
        for col in self.df2.columns:
            for key, value in self.column_mappings.items():
                if col == key:
                    break
                elif col in value:
                    self.df2.rename(columns={col: key}, inplace=True)
                    break


    def check_columns(self, columns_to_compare):
        self.check_column_formatting()
        columns_to_keep = []
        for col in columns_to_compare:
            if (col in self.df1.columns and col in self.df2.columns):
                if (col == 'ID'):
                    self.contains_ID = True
                columns_to_keep.append(col)
            else:
                if (col in self.df1.columns):
                    self.columns_dropped_message += f"COLUMN DROPPED: '{col}' is only present in file 1\n"
                    print("COLUMN DROPPED: '" + col + "' is only present in file 1")
                elif (col in self.df2.columns):
                    self.columns_dropped_message += f"COLUMN DROPPED: '{col}' is only present in file 2\n"
                    print("COLUMN DROPPED: '" + col + "' is only present in file 2")
                else:
                    self.columns_dropped_message += f"COLUMN DROPPED: '{col}' is not present in either file\n"
                    print("COLUMN DROPPED: '" + col + "' is not present in either file")
                if (col == 'ID'):
                    self.columns_dropped_message += "\tReplaced ID with Gene and AA_Change\n"
        if not self.contains_ID:
            can_replace = True
            for col in self.ID_replacement_cols:
                if col not in self.df1.columns or col not in self.df2.columns:
                    can_replace = False
            if can_replace:
                print("Replacing ID with Gene and AA Change")
                self.combine_gene_and_AA_change()
                columns_to_keep.append('ID')
                self.replaced_ID = True
        return columns_to_keep


    def combine_gene_and_AA_change(self):
        self.df1['ID'] = self.df1[self.ID_replacement_cols[0]].astype(str) + ' (' + self.df1[self.ID_replacement_cols[1]].astype(str) + ')'
        self.df2['ID'] = self.df2[self.ID_replacement_cols[0]].astype(str) + ' (' + self.df2[self.ID_replacement_cols[1]].astype(str) + ')'

        self.df1.drop(columns=self.ID_replacement_cols, inplace=True)
        self.df2.drop(columns=self.ID_replacement_cols, inplace=True)


    def drop_additional_columns(self):
        cols1_to_drop = [col for col in self.df1.columns if col not in self.columns_to_compare]
        cols2_to_drop = [col for col in self.df2.columns if col not in self.columns_to_compare]

        if cols1_to_drop:
            self.df1.drop(columns=cols1_to_drop, inplace=True)

        if cols2_to_drop:
            self.df2.drop(columns=cols2_to_drop, inplace=True)

        self.columns_to_compare.remove('ID')


    def make_rows_equal(self):
        num_rows_to_add = abs(self.df1.shape[0] - self.df2.shape[0])
        if self.df1.shape[0] > self.df2.shape[0]:
            dummy_data = pd.DataFrame(np.nan, index=range(num_rows_to_add), columns=self.df2.columns)
            self.df2 = pd.concat([self.df2, dummy_data], ignore_index=True)
        else:
            dummy_data = pd.DataFrame(np.nan, index=range(num_rows_to_add), columns=self.df1.columns)
            self.df1 = pd.concat([self.df1, dummy_data], ignore_index=True)


    @staticmethod
    def extract_parts_ID(id_str):
        match = re.match(r'chr(\w+)-(\d+)-(\d+)-', id_str)
        if match:
            chr_part = match.group(1)
            if chr_part.isdigit():
                chr_part = int(chr_part)
            else:
                chr_part = float('inf')
            return pd.Series([chr_part, int(match.group(2)), int(match.group(3))])
        return pd.Series([None, None, None])

    
    def sort_rows(self):
        if self.contains_ID:
            # Extract parts and create columns for sorting
            self.df1[['chr_num', 'num1', 'num2']] = self.df1['ID'].apply(self.extract_parts_ID)
            self.df2[['chr_num', 'num1', 'num2']] = self.df2['ID'].apply(self.extract_parts_ID)

            # Sort by the extracted columns
            self.df1.sort_values(by=['chr_num', 'num1', 'num2'], inplace=True)
            self.df2.sort_values(by=['chr_num', 'num1', 'num2'], inplace=True)

            # Reset the indices
            self.df1.reset_index(drop=True, inplace=True)
            self.df2.reset_index(drop=True, inplace=True)

            # Remove the temporary columns
            self.df1.drop(columns=['chr_num', 'num1', 'num2'], inplace=True)
            self.df2.drop(columns=['chr_num', 'num1', 'num2'], inplace=True)

        elif self.replaced_ID:
            temp_cols = self.df1['ID'].str.split('-', expand=True)
            self.df1['grp1'] = temp_cols[0]
            self.df1['grp2'] = temp_cols[1]
            self.df1.sort_values(by=['grp1', 'grp2'], inplace=True)
            self.df1.drop(columns=['grp1', 'grp2'], inplace=True)

            temp_cols = self.df2['ID'].str.split('-', expand=True)
            self.df2['grp1'] = temp_cols[0]
            self.df2['grp2'] = temp_cols[1]
            self.df2.sort_values(by=['grp1', 'grp2'], inplace=True)
            self.df2.drop(columns=['grp1', 'grp2'], inplace=True)