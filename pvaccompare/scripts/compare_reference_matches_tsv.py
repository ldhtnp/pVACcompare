from scripts.run_utils import *



class CompareReferenceMatchesTSV():
    def __init__(self, input_file1, input_file2, output_file):
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.output_path = output_file
        self.df1, self.df2 = load_tsv_files(self.input_file1, self.input_file2)
        self.columns_to_compare = ['Transcript', 'MT Epitope Seq', 'Peptide	Hit ID', 'Hit Definition']
        self.common_variants = set()
        self.unique_variants_file1 = set()
        self.unique_variants_file2 = set()
        self.differences = {}



    def generate_comparison_report(self):
        self.differences = get_file_differences(self.df1, self.df2, self.unique_variants_file1, self.unique_variants_file2, self.columns_to_compare)
        
        if self.differences:
            first_unique_variant1 = True
            first_unique_variant2 = True
            try:
                with open(self.output_path, 'a') as f:
                    f.write("\n\n============================== REFERENCE MATCH TSV COMPARISON ==============================\n\n\n")
                    f.write(f"File 1: {self.input_file1}\n")
                    f.write(f"File 2: {self.input_file2}\n")
                    # if self.columns_dropped_message != "":
                    #     f.write(f"\n{self.columns_dropped_message}")
                    # differences_summary = self.generate_differences_summary()
                    # f.write(differences_summary)
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
            except Exception as e:
                raise Exception(f"Error writing differences to file: {e}")
        else:
            print("The Reference Match TSV files are identical.")