import pandas as pd
import numpy as np
import re
import datetime


class CompareTSV():
    def __init__(self, input_file1, input_file2, output_path, columns_to_compare):
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.output_path = output_path
        df1 = pd.DataFrame()
        df2 = pd.DataFrame()
        try:
            df1 = pd.read_csv(input_file1, sep='\t')
            df2 = pd.read_csv(input_file2, sep='\t')
        except Exception as e:
            print(f"Error loading files: {e}")
        self.df1 = df1
        self.df2 = df2
        self.contains_ID = False
        self.differences = {}
        self.column_mappings = { # Fill in different names/formatting between versions
            'Best Peptide': ['best peptide', 'best_peptide'],
            'Best Transcript': ['best transcript', 'best_transcript'],
            'Tier': ['tier']
        }
        self.columns_to_compare = self.check_columns(columns_to_compare)
        self.common_ids = self.get_common_ids() if self.contains_ID else set()

    
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


    def get_unique_ids(self):
        unique_to_file1 = []
        unique_to_file2 = []
        for value in self.df1['ID'].values:
            if value not in self.common_ids and not pd.isna(value):
                unique_to_file1.append(value)
        
        for value in self.df2['ID'].values:
            if value not in self.common_ids and not pd.isna(value):
                unique_to_file2.append(value)
        return unique_to_file1, unique_to_file2


    def comparison_with_ID(self):
        unique_to_file1, unique_to_file2 = self.get_unique_ids()
        for value1 in self.df1['ID'].values:
            if value1 not in unique_to_file1:
                for value2 in self.df2['ID'].values:
                    if value2 not in unique_to_file2:
                        if (value1 == value2):
                            row_file1 = self.df1.loc[self.df1['ID'] == value1]
                            row_file2 = self.df2.loc[self.df2['ID'] == value2]
                            self.compare_rows_with_ID(row_file1, row_file2)

        if unique_to_file1 or unique_to_file2:
            if 'ID' not in self.differences:
                self.differences['ID'] = []
            for variant in unique_to_file1:
                self.differences['ID'].append({
                        'File 1': variant,
                        'File 2': ''
                    })
            for variant in unique_to_file2:
                self.differences['ID'].append({
                        'File 1': '',
                        'File 2': variant
                    }) 


    def comparison_without_ID(self):
        pass


    def generate_comparison_report(self):
        if (self.contains_ID):
            self.comparison_with_ID()
        else:
            self.comparison_without_ID()
        
        if self.differences:
            first_unique_variant1 = True
            first_unique_variant2 = True
            try:
                with open(self.output_path, 'w') as f:
                    f.write(f"Report Generation Date and Time: {datetime.datetime.now()}\n\n")
                    f.write(f"File 1: {self.input_file1}\n")
                    f.write(f"File 2: {self.input_file2}\n")
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
                                f.write(f"{diff['ID']}\t{diff['File 1']}\t{diff['File 2']}\n")
                print(f"Successfully generated comparison report.")
            except Exception as e:
                print(f"Error writing differences to file: {e}")
        else:
            print("The files are identical.")


    def get_common_ids(self):
        common_ids = set(self.df1['ID']).intersection(set(self.df2['ID']))
        return common_ids


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
            elif (col in self.df1.columns):
                print("COLUMN DROPPED: \'" + col + "\' is only present in file 1")
            elif (col in self.df2.columns):
                print("COLUMN DROPPED: \'" + col + "\' is only present in file 2")
            else:
                print("COLUMN DROPPED: \'" + col + "\' is not present in either file")
        if not self.contains_ID:
            # TODO: Add AA change and gene to columns to keep if ID not present?
            print("ID NOT FOUND")
        return columns_to_keep


    def drop_additional_columns(self):
        cols1_to_drop = [col for col in self.df1.columns if col not in self.columns_to_compare]
        cols2_to_drop = [col for col in self.df2.columns if col not in self.columns_to_compare]

        if cols1_to_drop:
            self.df1.drop(columns=cols1_to_drop, inplace=True)

        if cols2_to_drop:
            self.df2.drop(columns=cols2_to_drop, inplace=True)

        if self.contains_ID:
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
        # ID is a unique identifier present in all of the recent versions >3.0
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
        else:
            # TODO: Implement sorting by another method when ID is not present
            # "Gene" and "AA change"?
            pass