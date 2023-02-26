##requires values.py, effprop_opt.py, predict.py
##TODO gi_csv_in 'csv_out/all_cols_sample-peter.csv'
##TODO ers_w_cost = 'ON_ERS_w_cost_HF2.pkl'
##TODO ers_no_cost = 'ON_ERS_no_cost_NHF2.pkl'
##TODO gi_wp = 'GI_Weights_&_Points.csv'
##TODO cost_w_ers = 'ON_Cost_w_ERS_HF2.pkl'
##TODO max_rows = 100
##TODO out_folder
import pandas as pd
import pickle
from tqdm import tqdm
import argparse
from pathlib import Path
import sys
from optimize import *


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, help="path to the GI CSV file (rows to optimize)")
ap.add_argument("--mec", required=True, help="model: ERS with Cost")
ap.add_argument("--menc", required=True, help="model: ERS with NO Cost")
ap.add_argument("--mc", required=True, help="model: Cost with ERS")
ap.add_argument("--mref", required=False, help="model: Ref rating", default=None)
ap.add_argument("--giwp", required=False, help="path to GI_Weights_&_Points.csv", default='GI_Weights_&_Points.csv')
ap.add_argument("--maxrows", required=False, help="Max Rows to output", default=100)
ap.add_argument("--out", required=False, help="Output folder to place the .CSV files with optimizations", default='opt_out')
ap.add_argument("--ucost", required=False, help="A .CSV file with costs of upgrades", default=None)

args = vars(ap.parse_args())

gi_csv_in = args['input']
ers_w_cost = args['mec']
ers_no_cost = args['menc']
cost_w_ers = args['mc']
gi_wp = args['giwp']
max_rows = int(args['maxrows'])
out_folder = args['out']
ucostf = args['ucost']
mref = args['mref']

data = pd.read_csv(gi_csv_in)  # Read file into df

try:
    data['Postal Code'] = data['Postal Code'].str.slice(0, 1)
except:
    pass

try:
    Path(out_folder).mkdir(parents=True, exist_ok=True)
except:
    print("Cannot create the folder {}".format(out_folder))
    sys.exit(-1)

if ucostf:
    ucost = pd.read_csv(ucostf)
else:
    print("A .CSV file with costs of upgrades is not given. Upgrade cost won't be calculated")


outputs = []
with tqdm(total=len(data)) as pbar:
    for i in range(len(data)):
        orig = data[i:i+1]
        if 'unique_num' not in orig:  # If no unique_num column, exit script
            raise ValueError("Error: 'unique_num' column not found in the input file. Script will exit.")

        reductions, idx = get_ers_reductions(orig, 
                                             ers_w_cost, 
                                             ers_no_cost,
                                             gi_wp,
                                             mref)
        best_reducs = reductions[0:max_rows]
        out = calc_savings(orig, best_reducs, cost_w_ers, len(best_reducs))
        if ucostf:
            add_upgrade_cost(out, ucost)
            
        outputs.append((out, idx))
        pbar.update(1)


idx = 0
for out in outputs:
    print(out[0])
    out[0].to_csv("{}/{}_{}_{}.csv".format(out_folder, idx, out[1], "reductions"), index = False)
    idx += 1