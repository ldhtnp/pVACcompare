from scripts.run_utils import *



class CompareUnaggregatedTSV():
    def __init__(self, input_file1, input_file2, output_file):
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.output_path = output_file
        self.df1, self.df2 = load_tsv_files(self.input_file1, self.input_file2)
        self.columns_to_compare = ['Biotype', 'Sub-peptide Position', 'Median MT IC50 Score', 'Median WT IC50 Score', 'Median MT Percentile', 
        'Median WT Percentile', 'WT Epitope Seq', 'Tumor DNA VAF', 'Tumor RNA Depth', 'Tumor RNA VAF', 'Gene Expression']
        self.common_variants = set()
        self.unique_variants_file1 = set()
        self.unique_variants_file2 = set()
        self.differences = {}



    def create_id_column(self):
        id_columns = ['Chromosome', 'Start', 'Stop', 'Reference', 'Variant', 'HLA Allele', 'MT Epitope Seq']
        self.df1['ID'] = self.df1[id_columns].apply(lambda x: '-'.join(map(str, x)), axis=1)
        self.df2['ID'] = self.df2[id_columns].apply(lambda x: '-'.join(map(str, x)), axis=1)

        self.df1.drop(columns=id_columns, inplace=True)
        self.df2.drop(columns=id_columns, inplace=True)
    

    @staticmethod
    def output_dropped_cols(cols1_to_drop, cols2_to_drop):
        for col in cols1_to_drop:
            if col in cols2_to_drop:
                print(f"UNAGGREGATED COMPARISON DROPPED: '{col}' is not present in either file")
            else:
                print(f"UNAGGREGATED COMPARISON DROPPED: '{col}' is only present in file 1")
        for col in cols2_to_drop:
            if col not in cols1_to_drop:
                print(f"UNAGGREGATED COMPARISON DROPPED: '{col}' is only present in file 2")
    
    

    def generate_comparison_report(self):
        self.differences, self.unique_variants = get_file_differences(self.df1, self.df2, self.columns_to_compare, self.unique_variants_file1, self.unique_variants_file2)
        
        if self.differences or self.unique_variants:
            first_unique_variant1 = True
            first_unique_variant2 = True
            try:
                with open(self.output_path, 'a') as f:
                    f.write("\n\n============================== UNAGGREGATED TSV COMPARISON ==============================\n\n\n")
                    f.write(f"File 1: {self.input_file1}\n")
                    f.write(f"File 2: {self.input_file2}\n")
                    # if self.columns_dropped_message != "":
                    #     f.write(f"\n{self.columns_dropped_message}")
                    # differences_summary = self.generate_differences_summary()
                    # f.write(differences_summary)
                                
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
            print("The Unaggregated TSV files are identical.")