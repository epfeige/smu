# See README.md for info
import pandas as pd
import sys
import os
import datetime

# attr_1 = 'ERS Rating'
attr_1 = 'ERSRATING'
output_folder = 'new_rerun'

# Ensure output folder exists and add '/' to end of folder name if needed
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
if output_folder[len(output_folder)-1] != '/':
    output_folder = output_folder + '/'


# Get the current date
now = datetime.datetime.now()

def process_csv(file_name):
    # read csv file into a pandas dataframe
    df = pd.read_csv(file_name)
    unique = 'No'
    if df.columns[0] == 'unique_num':
        print('yes')
        unique = 'Yes'

    # count of original number of rows
    org_row_count = df.shape[0]

    # count of rows with a 0 in 'ERS Rating'
    zero_count = df[df[attr_1] == 0].shape[0]

    # count of rows with no value in 'ERS Rating'
    no_value = df[attr_1].isna().sum()

    # count of rows with goog values in 'ERS Rating'
    ok_value = df[df[attr_1] > 0].shape[0]

    # output file name
    base = os.path.basename(file_name)
    output_file = os.path.splitext(base)[0] + "_output.txt"

    base = os.path.basename(file_name)
    new_file_name = os.path.splitext(base)[0] + "_no_nan.csv"

    # write the counts to the output file
    with open(output_folder + output_file, 'w') as f:
        f.write(f"Date processed:  {now} \n\n")
        f.write(f"Output file without zeros or NaNs: {new_file_name}\n\n")
        f.write(f"Original file: {file_name}\n\n")
        f.write(f"Total number of rows: {org_row_count}\n")
        f.write(f"ERS with value zero: {zero_count}\n")
        f.write(f"ERS with no value: {no_value}\n")
        f.write(f"ERS with good value: {ok_value}\n\n")
        f.write(f"Total number of columns: {len(df.columns)}\n\n")
        f.write(f"Unique Identifier unique_row exists? {unique} \n")


    print(f"Output written to {output_folder + output_file}")


def remove_nan_rows(file_name):
    # read csv file into a pandas dataframe
    df = pd.read_csv(file_name)

    # remove rows where ERS Rating is zero or nan
    df = df[(df[attr_1] != 0) & (df[attr_1].notna())]

    # new file name
    base = os.path.basename(file_name)
    new_file_name = os.path.splitext(base)[0] + "_no_nan.csv"

    # write the modified dataframe to a new file
    df.to_csv(output_folder + new_file_name, index=False)

    print(f"Rows with ERS Rating zero or NaN removed. New file created: {output_folder + new_file_name}")


if __name__ == "__main__":
    file_name = sys.argv[1]
    process_csv(file_name)
    remove_nan_rows(file_name)
