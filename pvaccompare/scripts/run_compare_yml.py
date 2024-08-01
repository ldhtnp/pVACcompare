from scripts.compare_yml import CompareYML



def main(input_file1, input_file2, output_file):
    """
    Purpose:    Control function for the inputs.yml file comparison
    Modifies:   Nothing
    Returns:    None
    """
    comparer = CompareYML(input_file1, input_file2, output_file)

    if not comparer.differences:
        print("The YAML input files are identical.")
    else:
        try:
            comparer.interpret_diff()
        except Exception as e:
            print(f"Error occurred while generating input comparison report: {e}")



if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
