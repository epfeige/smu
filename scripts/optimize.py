##requires values.py, effprop_opt.py, predict.py
##TODO gi_csv_in 'csv_out/all_cols_sample-peter.csv'
##TODO ers_w_cost = 'ON_ERS_w_cost_HF2.pkl'
##TODO ers_no_cost = 'ON_ERS_no_cost_NHF2.pkl'
##TODO gi_wp = 'GI_Weights_&_Points.csv'
##TODO cost_w_ers = 'ON_Cost_w_ERS_HF2.pkl'
##TODO max_rows = 100
##TODO out_folder
from functools import reduce
import numpy as np
import pandas as pd
import pickle
from predict import predict_df, get_expected_features
import time
import copy
from effprop_opt import get_attributes_for_upgrade, update_mhf
import values
from tqdm import tqdm
import argparse
from pathlib import Path
import sys

def gen_rows(col_name, values):
    data = []
    for val in values:
        data.append((val,0))
    return pd.DataFrame.from_records(data, columns =[col_name, 'temp'])

def merge(data_frames):
    return reduce(lambda l, r: 
                  pd.merge(l, r, on=['temp']),
                  data_frames).drop(['temp'], axis=1)

def generate(original_row, frame):
    size = len(frame)
    rc = original_row.copy()
    while len(rc) <= size:
        rc = rc.append([rc]*2, ignore_index=True)
    rc = rc[0:size]
    
    for col in frame.columns:
        rc[col] = np.array(frame[col])
    return rc

def get_generated_df(row, values, upg_vals):
    sel_vals = []
    for val in values:
        if val[0] in upg_vals:
            sel_vals.append(val)
    augm_vals = copy.deepcopy(sel_vals)
    
    for val in augm_vals:
        s_val = row[val[0]].iloc[0]
        if s_val not in val[1]:
            val[1].append(s_val)

    combo_frame = merge(map(lambda values:
                        gen_rows(values[0], values[1]),
                        augm_vals))
    
        
    perms = generate(row, combo_frame)
    return perms

def get_ers_reductions(orig, model_ers_w_cost, model_ers_no_cost, gi_weights_and_points):
    id = 'no_id'
    if 'ID' in orig.columns:
        id = orig['ID'].iloc[0]
    upg_vals = get_attributes_for_upgrade(gi_weights_and_points, orig)
    orig_pred = predict_df(orig, model_ers_w_cost)  # row of original prediction
    original_ers = orig_pred['predicted'].iloc[0]  # actual ERS predicted with heating cost
    orig_pred_no_cost = predict_df(orig, model_ers_no_cost)
    original_ers_no_cost = orig_pred_no_cost['predicted'].iloc[0]
    ratio = original_ers/original_ers_no_cost
    
    #generate permutations
    df1 = get_generated_df(orig, all_vals, upg_vals)
    
    #exclude tot_hs > 100%
    perc_cols = []
    for hs in [*values.heat_pumps, *values.other_heat_system]:
        if hs[0] in df1.columns:
            col = hs[0]
            val = hs[1][0]
            new_col = col + '__%'
            df1[new_col] = df1[col]/val*100
            perc_cols.append(new_col)
    tot_hs = df1[perc_cols].sum(axis = 1)
    df1['tot_hs'] = tot_hs
    dfp = df1[df1['tot_hs'] <= 100]
    
    pred = predict_df(dfp, model_ers_no_cost)
    diff = pred[upg_vals].sub(list(orig_pred[upg_vals].to_numpy()[0]))
    nchanges = (diff != 0).sum(axis=1)
    pred['nchanges'] = nchanges
    pred['tot_hs'] = dfp.tot_hs
    pred['ratio'] = ratio
    pred['ers_diff'] = original_ers - pred['predicted']*ratio
    pred['reduction'] = pred['ers_diff']/pred['nchanges']
    pred = pred.rename(columns={"predicted": "ers_predicted"})
    pred['pred_ratio'] = pred['ers_predicted']*ratio
    
    ers_reductions = pred[pred['nchanges'] > 0].sort_values(by=['reduction'], ascending = False)
    orig_cpy = orig.copy()
    for col in ers_reductions:
        if col not in orig_cpy.columns:
            orig_cpy[col] = 'N/A'
    orig_cpy['ers_predicted'] = original_ers
    orig_cpy = orig_cpy[ers_reductions.columns.tolist()]
    ret_df = pd.concat([orig_cpy, ers_reductions])


    return ret_df, id

def calc_savings(orig, reductions_df, model_cost_w_ers, max_rows):
    reductions_df = reductions_df.copy()
    reduc = reductions_df[1: max_rows + 1].copy()
    reduc['ERS Rating'] = reduc['ers_predicted'] * reduc['ratio']
    reduc['Main Heating Fuel'] = orig['Main Heating Fuel'].iloc[0]
    update_mhf(reduc)
    new_cost = predict_df(reduc, model_cost_w_ers)['predicted']
    old_cost = predict_df(orig, model_cost_w_ers)['predicted']
    reduc['cost_savings'] = old_cost.iloc[0] - new_cost
    reductions_df['cost_savings'] = reduc['cost_savings']
    return reductions_df



ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,
   help="path to the GI CSV file (rows to optimize)")
ap.add_argument("--mec", required=True, help="model: ERS with Cost")
ap.add_argument("--menc", required=True, help="model: ERS with NO Cost")
ap.add_argument("--mc", required=True, help="model: Cost with ERS")
ap.add_argument("--giwp", required=False, help="path to GI_Weights_&_Points.csv",
               default='GI_Weights_&_Points.csv')
ap.add_argument("--maxrows", required=False, help="Max Rows to output",
               default=100)
ap.add_argument("--out", required=False, 
                help="Output folder to place the .CSV files with optimizations",
               default='opt_out')
args = vars(ap.parse_args())

gi_csv_in = args['input']
ers_w_cost = args['mec']
ers_no_cost = args['menc']
cost_w_ers = args['mc']
gi_wp = args['giwp']
max_rows = args['maxrows']
out_folder = args['out']

data = pd.read_csv(gi_csv_in)
try:
    data['Postal Code'] = data['Postal Code'].str.slice(0, 1)
except:
    pass

try:
    Path(out_folder).mkdir(parents=True, exist_ok=True)
except:
    print("Cannot create the folder {}".format(out_folder))
    sys.exit(-1)

all_vals = [*values.heat_pumps,          
            *values.heating_support,
            *values.building_env,
            *values.water_heating, 
            *values.other_heat_system,
            *values.energy_prod]

outputs = []
with tqdm(total=len(data)) as pbar:
    for i in range(len(data)):
        orig = data[i:i+1]
        reductions, idx = get_ers_reductions(orig, 
                                             ers_w_cost, 
                                             ers_no_cost,
                                             gi_wp)
        best_reducs = reductions[0:max_rows]
        out = calc_savings(orig, best_reducs, cost_w_ers, len(best_reducs))
        outputs.append((out, idx))
        pbar.update(1)


idx = 0
for out in outputs:
    out[0].to_csv("{}/{}_{}_{}.csv".format(out_folder, out[1], idx, "reductions"), index = False)
    idx += 1