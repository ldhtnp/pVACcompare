import pandas as pd
import numpy as np


class RunUtils():
    def __init__(self, output_path):
        self.output_path = output_path
    

    @staticmethod
    def get_common_variants(df1, df2):
        return set(df1['ID']).intersection(set(df2['ID']))


    @staticmethod
    def load_tsv_files(input_file1, input_file2):
        try:
            df1 = pd.read_csv(input_file1, sep='\t', low_memory=False)
            df2 = pd.read_csv(input_file2, sep='\t', low_memory=False)
        except Exception as e:
            raise Exception(f"Error loading files: {e}")
        return df1, df2
    

    @staticmethod
    def make_rows_equal(df1, df2):
        num_rows_to_add = abs(df1.shape[0] - df2.shape[0])
        if df1.shape[0] > df2.shape[0]:
            dummy_data = pd.DataFrame(np.nan, index=range(num_rows_to_add), columns=df2.columns)
            df2 = pd.concat([df2, dummy_data], ignore_index=True)
        else:
            dummy_data = pd.DataFrame(np.nan, index=range(num_rows_to_add), columns=df1.columns)
            df1 = pd.concat([df1, dummy_data], ignore_index=True)
        return df1, df2
    

    @staticmethod
    def get_unique_variants(df1, df2, common_variants):
        unique_variants_file1 = set()
        unique_variants_file2 = set()
        for value in df1['ID'].values:
            if value not in common_variants and not pd.isna(value):
                unique_variants_file1.add(value)
        
        for value in df2['ID'].values:
            if value not in common_variants and not pd.isna(value):
                unique_variants_file2.add(value)
        return unique_variants_file1, unique_variants_file2
    

    @staticmethod
    def compare_rows_with_ID(row_file1, row_file2, columns_to_compare, differences):
        for col in columns_to_compare:
            value_file1 = row_file1[col].values[0]
            value_file2 = row_file2[col].values[0]
            if value_file1 != value_file2:
                if col not in differences:
                    differences[col] = []
                differences[col].append({
                    'ID': row_file1['ID'].values[0],
                    'File 1': value_file1,
                    'File 2': value_file2
                })
        return differences


    @staticmethod
    def get_file_differences(df1, df2, unique_variants_file1, unique_variants_file2, columns_to_compare):
        differences = {}
        for value1 in df1['ID'].values:
            if value1 not in unique_variants_file1:
                for value2 in df2['ID'].values:
                    if value2 not in unique_variants_file2:
                        if (value1 == value2):
                            row_file1 = df1.loc[df1['ID'] == value1]
                            row_file2 = df2.loc[df2['ID'] == value2]
                            differences = RunUtils.compare_rows_with_ID(row_file1, row_file2, columns_to_compare, differences)

        if unique_variants_file1 or unique_variants_file2:
            if 'ID' not in differences:
                differences['ID'] = []
            for variant in unique_variants_file1:
                differences['ID'].append({
                        'File 1': variant,
                        'File 2': ''
                    })
            for variant in unique_variants_file2:
                differences['ID'].append({
                        'File 1': '',
                        'File 2': variant
                    })
        return differences