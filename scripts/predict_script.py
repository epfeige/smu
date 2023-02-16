import pandas as pd
from pandas import DataFrame
import pickle
import argparse
import sys
import os


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--model", required=True,
   help="path to load the model (e.g., mymodel.pkl)")
ap.add_argument("-p", "--features", action="store_true",
   help="print features required for the model")
ap.add_argument("-f", "--csv", default="none",
   help="path to the CSV file with data to predict")
ap.add_argument('--no_header', action="store_true",
                help='indicate whether the csv file does not have a header')

args = vars(ap.parse_args())
data_path = args['csv']
pkl_filename = args['model']
has_header = not args['no_header']

if not args['features'] and data_path == "none":
    print("Error: You must specify path to the .csv file with data to predict")
    exit(-1)

with open(pkl_filename, 'rb') as file:
    estimator = pickle.load(file)

if args['features']:
    print("required attributes:")
    print(list(estimator[1]))
    if data_path == "none":
        exit(0)

if has_header:
    #fts = get_expected_features(pkl_filename)
    df = pd.read_csv(data_path)
    postal_code = df['Postal Code'].copy()  # create a copy of the postal code for later reference
    df['Postal Code'] = df['Postal Code'].astype(str).str[0]
    print(postal_code)
    print(df.head(3))
    ERS = df['ERS Rating']
    columns_to_check = list(estimator[1])
    missing_columns = set(columns_to_check) - set(df.columns)
    if missing_columns:
        print("The input file: " + data_path + " misses these columns: " + str(list(missing_columns)))
        sys.exit()
    if 'unique_num' in df.columns:
        print('YES')
        unique_num_column = df['unique_num']
        df.drop(columns=['unique_num'], inplace=True)  # remove 'unique_num' column
    else:
        unique_num_column = None

    df = df[list(estimator[1])]
    # column_name = "Total Heating Cost"
    # df[column_name] = df[column_name].astype(int)

else:
    df = pd.read_csv(data_path, header = None)
    df.columns = estimator[1]
    unique_num_column = None


predicted = estimator[0].predict(df)   
df['predicted'] = predicted
df['ERS Rating'] = ERS

if unique_num_column is not None:
    print("----- insert unique_num")
    df.insert(0, 'unique_num', unique_num_column)  # add 'unique_num' column back to the output dataframe

df.insert(1, 'Org. Postal Code', postal_code)  # add full postal code back to the output dataframe
# output file name
base = os.path.basename(data_path)
output_file = os.path.splitext(base)[0] + "_pred.csv"

# output folder
out_folder = "../data/gi_data/GI_with_predictions/"  # Default
# out_folder = ""  # Choose your own.
df.to_csv(out_folder + output_file, index = False)
print("-- Done -- \n")
print("-- Saved as: " + output_file + " in: " + output_file + " -- \n\n")


