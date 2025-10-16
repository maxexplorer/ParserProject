# main.py

import os
from processor import process_all_csv

def main():
    input_folder = os.path.join(os.getcwd(), "data")
    output_folder = os.path.join(os.getcwd(), "results")

    process_all_csv(input_folder, output_folder)

if __name__ == "__main__":
    main()
