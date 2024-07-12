import pandas as pd
import numpy as np
import re
from multiprocessing import Pool



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



def create_id_column(df1, df2):
    id_columns = ['Chromosome', 'Start', 'Stop', 'Reference', 'Variant']
    df1['ID'] = df1[id_columns].apply(lambda x: '-'.join(map(str, x)), axis=1)
    df2['ID'] = df2[id_columns].apply(lambda x: '-'.join(map(str, x)), axis=1)

    df1.drop(columns=id_columns, inplace=True)
    df2.drop(columns=id_columns, inplace=True)



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



def compare_rows_with_id(args):
    row_file1, row_file2, columns_to_compare = args
    differences = {}
    for col in columns_to_compare:
        value_file1 = row_file1[col].values[0] if not row_file1.empty else None
        value_file2 = row_file2[col].values[0] if not row_file2.empty else None

        if pd.isna(value_file1) and pd.isna(value_file2):
            continue

        if value_file1 != value_file2:
            if col not in differences:
                differences[col] = []
            differences[col].append({
                'ID': row_file1['ID'].values[0] if not row_file1.empty else row_file2['ID'].values[0],
                'File 1': value_file1,
                'File 2': value_file2
            })
    return differences



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



def get_file_differences(df1, df2, unique_variants_file1, unique_variants_file2, columns_to_compare, contains_id=True):
    common_ids = set(df1['ID']).intersection(set(df2['ID'])).difference(unique_variants_file1).difference(unique_variants_file2)
    
    with Pool() as pool:
        args = [(df1.loc[df1['ID'] == cid], df2.loc[df2['ID'] == cid], columns_to_compare) for cid in common_ids]
        results = pool.map(compare_rows_with_id, args)

    differences = {}
    for result in results:
        for col, diffs in result.items():
            if col not in differences:
                differences[col] = []
            differences[col].extend(diffs)

    # Sort the differences for each column based on 'ID'
    for col in differences:
        if contains_id:
            differences[col] = sorted(differences[col], key=lambda x: extract_id_parts(x['ID']))
        else:
            differences[col] = sorted(differences[col], key=lambda x: split_replaced_id(x['ID']))
    
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

    # Sort 'ID' differences
    if 'ID' in differences:
        if contains_id:
            differences['ID'] = sorted(differences['ID'], key=lambda x: extract_id_parts(x['File 1'] or x['File 2']))
        else:
            differences['ID'] = sorted(differences['ID'], key=lambda x: split_replaced_id(x['File 1'] or x['File 2']))

    return differences