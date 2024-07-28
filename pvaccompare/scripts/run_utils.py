import pandas as pd
import numpy as np
import re



def get_common_variants(df1, df2):
    return set(df1['ID']).intersection(set(df2['ID']))



def load_tsv_files(input_file1, input_file2):
    try:
        df1 = pd.read_csv(input_file1, sep='\t', low_memory=False)
        df2 = pd.read_csv(input_file2, sep='\t', low_memory=False)
    except Exception as e:
        raise Exception(f"Error loading files: {e}")
    return df1, df2



def make_rows_equal(df1, df2):
    num_rows_to_add = abs(df1.shape[0] - df2.shape[0])
    if df1.shape[0] > df2.shape[0]:
        dummy_data = pd.DataFrame(np.nan, index=range(num_rows_to_add), columns=df2.columns)
        df2 = pd.concat([df2, dummy_data], ignore_index=True)
    else:
        dummy_data = pd.DataFrame(np.nan, index=range(num_rows_to_add), columns=df1.columns)
        df1 = pd.concat([df1, dummy_data], ignore_index=True)
    return df1, df2



def drop_useless_columns(df1, df2, columns_to_compare):
    columns_to_keep = set(['ID'])
    if 'ID' not in df1.columns or 'ID' not in df2.columns:
        columns_to_keep.update(['Gene', 'AA Change'])

    # Drop columns that are not in columns_to_compare and not 'ID'
    cols1_to_drop = [col for col in df1.columns if (col not in columns_to_compare) and (col not in columns_to_keep)]
    cols2_to_drop = [col for col in df2.columns if (col not in columns_to_compare) and (col not in columns_to_keep)]

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
    columns_to_keep = []
    for col in columns_to_compare:
        if col in df1.columns and col in df2.columns:
            columns_to_keep.append(col)
    return columns_to_keep



def get_unique_variants(df1, df2, common_variants):
    unique_variants_file1 = set(df1['ID']).difference(common_variants)
    unique_variants_file2 = set(df2['ID']).difference(common_variants)
    return unique_variants_file1, unique_variants_file2



def extract_id_parts(id_str):
    match = re.match(r'chr(\w+)-(\d+)-(\d+)-', id_str)
    if match:
        chr_part = match.group(1)
        if chr_part.isdigit():
            chr_part = int(chr_part)
        else:
            chr_part = float('inf')
        return chr_part, int(match.group(2)), int(match.group(3))
    return None, None, None



def split_replaced_id(id_str):
    try:
        grp1, rest = id_str.split(' (')
        grp2 = rest.split('-')[0].rstrip(')')
        return grp1, grp2
    except Exception as e:
        print(f"Error splitting replaced ID: {id_str}, {e}")
        return '', ''



def get_file_differences(df1, df2, columns_to_compare, unique_variants_file1, unique_variants_file2, contains_id=True, tolerance=0.1):
    merged_df = pd.merge(df1, df2, on='ID', suffixes=('_file1', '_file2'))
    
    differences = {}
    for col in columns_to_compare:
        col_file1 = f"{col}_file1"
        col_file2 = f"{col}_file2"
        
        mask = (merged_df[col_file1].notna() | merged_df[col_file2].notna()) & (merged_df[col_file1] != merged_df[col_file2])
        if np.issubdtype(merged_df[col_file1].dtype, np.number) and np.issubdtype(merged_df[col_file2].dtype, np.number):
            mask = mask | (np.abs(merged_df[col_file1] - merged_df[col_file2]) > tolerance)
        
        diff = merged_df[mask][['ID', col_file1, col_file2]]
        if not diff.empty:
            differences[col] = diff.to_dict('records')
    
    for col in differences:
        if contains_id:
            differences[col] = sorted(differences[col], key=lambda x: extract_id_parts(x['ID']))
        else:
            differences[col] = sorted(differences[col], key=lambda x: split_replaced_id(x['ID']))
    
    unique_variants = []
    # Include unique variants
    if unique_variants_file1 or unique_variants_file2:
        for variant in unique_variants_file1:
            unique_variants.append({
                'File 1': variant,
                'File 2': ''
            })
        for variant in unique_variants_file2:
            unique_variants.append({
                'File 1': '',
                'File 2': variant
            })
    
    # Sort unique variants
    if contains_id:
        unique_variants = sorted(unique_variants, key=lambda x: extract_id_parts(x['File 1'] if x['File 1'] else x['File 2']))
    else:
        unique_variants = sorted(unique_variants, key=lambda x: split_replaced_id(x['File 1'] if x['File 1'] else x['File 2']))
    
    return differences, unique_variants