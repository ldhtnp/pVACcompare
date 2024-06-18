import pandas as pd
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
        self.column_mappings = {
            'best peptide': []
        }
        self.columns_to_compare = self.check_columns(columns_to_compare)
        self.unique_rows = self.get_unique_rows()


    def comparison_with_ID(self, col_indices):
        differences = {}
        rows = self.df1.shape[0]
        for i in range(rows):
            for col_idx, col in zip(col_indices, self.columns_to_compare):
                # TODO: Need a different system for checking IDs, can have same number of rows but IDs might be different
                value1 = self.df1.iloc[i, col_idx]
                value2 = self.df2.iloc[i, col_idx]

                # Skip if both values are NaN
                if pd.isna(value1) and pd.isna(value2):
                    continue

                # Convert values to string for comparison
                value1_str = str(value1)
                value2_str = str(value2)

                if value1_str != value2_str:
                    if col == "ID":
                        if col not in differences:
                            differences[col] = []
                        differences[col].append({
                            'File 1': value1_str,
                            'File 2': value2_str
                        })
                    else:
                        if self.df1.loc[i, 'ID'] == self.df2.loc[i, 'ID']:
                            if col not in differences:
                                differences[col] = []
                            differences[col].append({
                                'ID': self.df1.loc[i, 'ID'],
                                'File 1': value1_str,
                                'File 2': value2_str
                            })
                        # else:
                        #     differences["ID"].append({
                        #         'File 1': value1_str,
                        #         'File 2': value2_str
                        #     })
        return differences


    def comparison_without_ID(self, col_indices):
        pass


    def compare_dataframes(self):
        # Get column indices for columns to compare
        col_indices = [self.df1.columns.get_loc(col) for col in self.columns_to_compare]

        differences = {}
        if (self.contains_ID):
            differences = self.comparison_with_ID(col_indices)
        else:
            differences = self.comparison_without_ID(col_indices)
        
        if differences:
            try:
                with open(self.output_path, 'w') as f:
                    f.write(f"Report Generation Date and Time: {datetime.datetime.now()}\n\n")
                    f.write(f"File 1: {self.input_file1}\n")
                    f.write(f"File 2: {self.input_file2}\n")
                    for col, diffs in differences.items():
                        if col != "ID":
                            f.write(f"\n\n============[ DIFFERENCES IN {col.upper()} ]============\n\n\n")
                            f.write("ID\tFile 1\tFile 2\n")
                            for diff in diffs:
                                f.write(f"{diff['ID']}\t{diff['File 1']}\t{diff['File 2']}\n")
                        else:
                            f.write(f"\n\n============[ UNIQUE VARIANTS ]============\n\n\n")
                            f.write("File 1\tFile 2\n")
                            for diff in diffs:
                                f.write(f"{diff['File 1']}\t{diff['File 2']}\n")
                print(f"\nSuccessfully generated comparison report.")
            except Exception as e:
                print(f"Error writing differences to file: {e}")
        else:
            print("The files are identical.")


    def check_columns(self, columns_to_compare):
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


    def drop_unique_rows(self):
        unique_rows = []
        if self.contains_ID:
            if self.df1.shape[0] > self.df2.shape[0]:
                for row1 in self.df1['ID']:
                    row_found = False
                    for row2 in self.df2['ID']:
                        if (row1 == row2):
                            row_found = True
                            break
                    if not row_found:
                        print(row1)
                        unique_rows.append(row1)
            else:
                for row1 in self.df2['ID']:
                    row_found = False
                    for row2 in self.df1['ID']:
                        if (row1 == row2):
                            row_found = True
                            break
                    if not row_found:
                        print(row1)
                        unique_rows.append(row1)
        else:
            # TODO
            pass
        return unique_rows


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
            # Susanna suggested grouping by "Gene" and "AA change"
            pass