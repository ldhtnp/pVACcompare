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
        """
        Purpose:    Combines multiple columns into a singular unique ID column in both dataframes
        Modifies:   df1 and df2
        Returns:    None
        """
        id_columns = ['Chromosome', 'Start', 'Stop', 'Reference', 'Variant', 'HLA Allele', 'MT Epitope Seq', 'Index']
        self.df1['ID'] = self.df1[id_columns].apply(lambda x: '-'.join(map(str, x)), axis=1)
        self.df2['ID'] = self.df2[id_columns].apply(lambda x: '-'.join(map(str, x)), axis=1)

        self.df1.drop(columns=id_columns, inplace=True)
        self.df2.drop(columns=id_columns, inplace=True)