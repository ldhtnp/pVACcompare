import pandas as pd
import datetime
import argparse


class CompareTSV():
    def __init__(self, input_file1, input_file2, output_path, columns_to_keep):
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
        self.columns_to_keep = columns_to_keep


    def compare_dataframes(self):
        # Get column indices for columns to compare
        col_indices = [self.df1.columns.get_loc(col) for col in self.columns_to_keep]

        differences = {}
        rows = self.df1.shape[0]
        for i in range(rows):
            for col_idx, col in zip(col_indices, self.columns_to_keep):
                value1 = self.df1.iloc[i, col_idx]
                value2 = self.df2.iloc[i, col_idx]

                # Skip if both values are NaN
                if pd.isna(value1) and pd.isna(value2):
                    continue

                # Convert values to string for comparison
                value1_str = str(value1)
                value2_str = str(value2)
                
                if value1_str != value2_str:
                    if col not in differences:
                        differences[col] = []
                    
                    differences[col].append({
                        'ID': self.df1.loc[i, 'ID'],
                        'File 1': value1_str,
                        'File 2': value2_str
                    })
        if differences:
            try:
                with open(self.output_path, 'w') as f:
                    f.write(f"Report Generation Date and Time: {datetime.datetime.now()}\n\n")
                    f.write(f"File 1: {self.input_file1}\n")
                    f.write(f"File 2: {self.input_file2}\n")
                    for col, diffs in differences.items():
                        f.write(f"\n\n============[ DIFFERENCES IN {col.upper()} ]============\n\n\n")
                        f.write("ID\tFile 1\tFile 2\n")
                        for diff in diffs:
                            f.write(f"{diff['ID']}\t{diff['File 1']}\t{diff['File 2']}\n")
                print(f"Successfully generated differences report.")
            except Exception as e:
                print(f"Error writing differences to file: {e}")
        else:
            print("The files are identical.")


    def check_columns(self):
        # TODO: Add check for ID, if not present add Gene and AA change
        columns_to_keep = []
        for col in self.columns_to_keep:
            if (col in self.df1.columns and col in self.df2.columns):
                columns_to_keep.append(col)
        self.columns_to_keep = columns_to_keep


    def drop_additional_columns(self):
        self.check_columns()
        cols1_to_drop = [col for col in self.df1.columns if col not in self.columns_to_keep]
        cols2_to_drop = [col for col in self.df2.columns if col not in self.columns_to_keep]

        if cols1_to_drop:
            self.df1.drop(columns=cols1_to_drop, inplace=True)

        if cols2_to_drop:
            self.df2.drop(columns=cols2_to_drop, inplace=True)


    def drop_additional_rows(self):
        added_rows1 = self.df1.index.difference(self.df2.index).tolist()
        added_rows2 = self.df2.index.difference(self.df1.index).tolist()
        
        if not added_rows1.empty:
            print("\n=== ROWS UNIQUE TO FILE 1 ===\n")
            for row in added_rows1:
                print(row+2)
        
        if not added_rows2.empty:
            print("\n=== ROWS UNIQUE TO FILE 2 ===\n")
            for row in added_rows2:
                print(row+2)
        return added_rows1, added_rows2

    
    def sort_rows(self):
        # ID is a unique identifier present in all of the recent versions >3.0
        if 'ID' in self.df1.columns and 'ID' in self.df2.columns:
            # Create a new temporary column for sorting by chromosome number
            self.df1['ID_numeric'] = self.df1['ID'].str.extract(r'chr(\d+)')
            self.df2['ID_numeric'] = self.df2['ID'].str.extract(r'chr(\d+)')
            self.df1['ID_numeric'] = pd.to_numeric(self.df1['ID_numeric'])
            self.df2['ID_numeric'] = pd.to_numeric(self.df2['ID_numeric'])

            # Sort by the temporary column
            self.df1.sort_values(by='ID_numeric', inplace=True)
            self.df2.sort_values(by='ID_numeric', inplace=True)

            # Removes the temporary column
            self.df1.drop(columns=['ID_numeric'], inplace=True)
            self.df2.drop(columns=['ID_numeric'], inplace=True)

            # Resetting indices after sorting
            self.df1.reset_index(drop=True, inplace=True)
            self.df2.reset_index(drop=True, inplace=True)
        else:
            # TODO: Implement sorting by another method when ID is not present
            # Susanna suggested grouping by "Gene" and "AA change"
            pass


def main(args):
    parser = argparse.ArgumentParser(description="Compare two TSV files and output differences.")
    parser.add_argument("input_file1", help="Path to the first TSV file")
    parser.add_argument("input_file2", help="Path to the second TSV file")
    parser.add_argument("output_file", help="Path to the output TSV file")
    
    parsed_args = parser.parse_args(args)
    file1_path = parsed_args.input_file1
    file2_path = parsed_args.input_file2
    output_path = parsed_args.output_file

    # Susanna stated number of variants, best peptide selected, best transcript select, and tier
    # TODO: Add this as a parameter to the command?
    columns_to_keep = ['ID', 'Best Peptide', 'Best Transcript', 'Tier']

    comparer = CompareTSV(file1_path, file2_path, output_path, columns_to_keep)
    comparer.drop_additional_columns()
    comparer.sort_rows()

    if (comparer.df1.shape == comparer.df2.shape):
        comparer.compare_dataframes()
    else: # Number of rows is not equal
        comparer.drop_additional_rows()

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
