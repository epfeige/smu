import pandas as pd
from pandas import DataFrame
import pickle
import argparse


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
    df = df[list(estimator[1])]
else:
    df = pd.read_csv(data_path, header = None)
    df.columns = estimator[1]
predicted = estimator[0].predict(df)   
df['predicted'] = predicted
df.to_csv(data_path + "__out.csv", index = False)
print("done")


