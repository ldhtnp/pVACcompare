
class RunUtils():
    def __init__(self, output_path):
        self.output_path = output_path
        self.common_rows = set()
    
    def fill_common_rows(self, df1, df2):
        self.common_rows = set(df1['ID']).intersection(set(df2['ID']))