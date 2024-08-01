from scripts.run_utils import *



class CompareReferenceMatchesTSV():
    def __init__(self, input_file1, input_file2, output_file):
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.output_path = output_file
        self.df1, self.df2 = load_tsv_files(self.input_file1, self.input_file2)
        self.columns_to_compare = ['Peptide', 'Match Window']
        self.hits_file1 = {}
        self.hits_file2 = {}
        self.common_variants = set()
        self.unique_variants_file1 = set()
        self.unique_variants_file2 = set()
        self.differences = {}



    def create_id_column(self):
        """
        Purpose:    Combines multiple columns into a singular unique ID column in both dataframes
        Modifies:   df1 and df2
        Returns:    None
        """
        id_columns = ['Chromosome', 'Start', 'Stop', 'Reference', 'Variant', 'Transcript', 'MT Epitope Seq', 'Hit ID', 'Match Start', 'Match Stop']
        self.df1['ID'] = self.df1[id_columns].apply(lambda x: '-'.join(map(str, x)), axis=1)
        self.df2['ID'] = self.df2[id_columns].apply(lambda x: '-'.join(map(str, x)), axis=1)

        self.df1.drop(columns=id_columns, inplace=True)
        self.df2.drop(columns=id_columns, inplace=True)
    


    def get_hit_count(self):
        self.hits_file1 = self.df1['ID'].value_counts().to_dict()
        self.hits_file2 = self.df2['ID'].value_counts().to_dict()
    


    # TODO: Potentially remove and used shared function in run_utils
    def compare_rows(self):
        for variant in self.common_variants:
            df1_rows = self.df1[self.df1['ID'] == variant]
            df2_rows = self.df2[self.df2['ID'] == variant]
            
            for _, row1 in df1_rows.iterrows():
                found = False
                for _, row2 in df2_rows.iterrows():
                    if all(row1[col] == row2[col] for col in self.columns_to_compare):
                        found = True
                        break
                if not found:
                    if variant not in self.differences:
                        self.differences[variant] = []
                    self.differences[variant].append({
                        'File': 'File 1',
                        'ID': row1['ID'],
                        'Hit ID': row1['Hit ID'],
                        'Match Sequence': row1['Match Sequence'],
                        'Query Sequence': row1['Query Sequence']
                    })

            for _, row2 in df2_rows.iterrows():
                found = False
                for _, row1 in df1_rows.iterrows():
                    if all(row2[col] == row1[col] for col in self.columns_to_compare):
                        found = True
                        break
                if not found:
                    if variant not in self.differences:
                        self.differences[variant] = []
                    self.differences[variant].append({
                        'File': 'File 2',
                        'ID': row2['ID'],
                        'Hit ID': row2['Hit ID'],
                        'Match Sequence': row2['Match Sequence'],
                        'Query Sequence': row2['Query Sequence']
                    })

    

    # TODO: Potentially remove and used shared function in run_utils
    def get_file_differences(self):
        self.compare_rows()

        # Sort the differences for each column based on 'ID'
        for col in self.differences:
            self.differences[col] = sorted(self.differences[col], key=lambda x: extract_id_parts(x['ID']))
        
        if self.unique_variants_file1 or self.unique_variants_file2:
            if 'ID' not in self.differences:
                self.differences['ID'] = []
            for variant in self.unique_variants_file1:
                self.differences['ID'].append({
                        'File 1': f"{variant}\t:\t{self.hits_file1[variant]}",
                        'File 2': ''
                    })
            for variant in self.unique_variants_file2:
                self.differences['ID'].append({
                        'File 1': '',
                        'File 2': f"{variant}\t:\t{self.hits_file2[variant]}"
                    })

        # Sort 'ID' differences
        if 'ID' in self.differences:
            file1_diffs = [diff for diff in self.differences['ID'] if diff['File 1']]
            file2_diffs = [diff for diff in self.differences['ID'] if diff['File 2']]
            
            file1_diffs = sorted(file1_diffs, key=lambda x: extract_id_parts(x['File 1']))
            file2_diffs = sorted(file2_diffs, key=lambda x: extract_id_parts(x['File 2']))
            
            self.differences['ID'] = file1_diffs + file2_diffs