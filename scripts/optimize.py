from functools import reduce
import numpy as np
import pandas as pd
import pickle
from predict import predict_df, get_expected_features
import time
import copy
from effprop_opt import get_attributes_for_upgrade, update_mhf
import values
from pathlib import Path
import sys
import ast


def gen_rows(col_name, values):
    data = []
    for val in values:
        data.append((val, 0))
    return pd.DataFrame.from_records(data, columns=[col_name, 'temp'])


def merge(data_frames):
    return reduce(lambda l, r:
                  pd.merge(l, r, on=['temp']),
                  data_frames).drop(['temp'], axis=1)


def generate(original_row, frame):
    size = len(frame)
    rc = original_row.copy()
    while len(rc) <= size:
        rc = rc.append([rc] * 2, ignore_index=True)
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


def get_ers_reductions(orig, model_ers_w_cost, model_ers_no_cost, gi_weights_and_points, model_ref=None):
    id = 'no_id'
    if 'ID' in orig.columns:
        id = orig['ID'].iloc[0]

    orig_pred = predict_df(orig, model_ers_w_cost)
    upg_vals = get_attributes_for_upgrade(gi_weights_and_points, orig)
    original_ers = orig_pred['predicted'].iloc[0]
    orig_pred_no_cost = predict_df(orig, model_ers_no_cost)
    original_ers_no_cost = orig_pred_no_cost['predicted'].iloc[0]
    ratio = original_ers / original_ers_no_cost

    if model_ref:
        orig_ref = predict_df(orig, model_ref)['predicted'].iloc[0]
    else:
        orig_ref = None

    # generate permutations
    df1 = get_generated_df(orig, all_vals, upg_vals)

    # exclude tot_hs > 100%
    perc_cols = []
    for hs in [*values.heat_pumps, *values.other_heat_system]:
        if hs[0] in df1.columns:
            col = hs[0]
            val = hs[1][0]
            new_col = col + '__%'
            df1[new_col] = df1[col] / val * 100
            perc_cols.append(new_col)
    tot_hs = df1[perc_cols].sum(axis=1)
    df1['tot_hs'] = tot_hs
    dfp = df1[df1['tot_hs'] <= 100]

    pred = predict_df(dfp, model_ers_no_cost)
    diff = pred[upg_vals].sub(list(orig_pred[upg_vals].to_numpy()[0]))
    nchanges = (diff != 0).sum(axis=1)
    pred['nchanges'] = nchanges
    pred['changes'] = (diff != 0).apply(lambda x: list(map(lambda y: upg_vals[y],
                                                           [i for i, v in enumerate(x) if v == True])), axis=1)
    pred['tot_hs'] = dfp.tot_hs
    pred['ratio'] = ratio
    pred['ers_diff'] = original_ers - pred['predicted'] * ratio
    pred['reduction'] = pred['ers_diff'] / pred['nchanges']
    pred = pred.rename(columns={"predicted": "ers_predicted"})

    ers_reductions = pred[pred['nchanges'] > 0].sort_values(by=['reduction'], ascending=False)
    orig_cpy = orig.copy()
    for col in ers_reductions:
        if col not in orig_cpy.columns:
            orig_cpy[col] = 'N/A'
    orig_cpy['ers_predicted'] = original_ers
    orig_cpy['ref'] = orig_ref
    ers_reductions['ref'] = 'N/A'
    orig_cpy = orig_cpy[ers_reductions.columns.tolist()]
    ret_df = pd.concat([orig_cpy, ers_reductions])

    return ret_df, id


def calc_savings(orig, reductions_df, model_cost_w_ers, max_rows, first=False):
    reductions_df = reductions_df.copy()
    reduc = reductions_df[0 if first else 1: max_rows + 1].copy()
    reduc['ERS Rating'] = reduc['ers_predicted'] * reduc['ratio']
    reduc['Main Heating Fuel'] = orig['Main Heating Fuel'].iloc[0]
    update_mhf(reduc)
    reductions_df['Main Heating Fuel'] = reduc['Main Heating Fuel']
    new_cost = predict_df(reduc, model_cost_w_ers)['predicted']
    old_cost = predict_df(orig, model_cost_w_ers)['predicted']
    reductions_df['cost_predicted'] = new_cost
    reduc['cost_savings'] = old_cost.iloc[0] - new_cost
    reductions_df['cost_savings'] = reduc['cost_savings']
    # reductions_df.iat[0, reductions_df.columns.get_loc('cost_predicted')] = old_cost.iloc[0]
    reductions_df.iat[0, reductions_df.columns.get_loc('Main Heating Fuel')] = orig['Main Heating Fuel'].iloc[0]
    reductions_df['old_cost'] = old_cost.iloc[0]

    return reductions_df


# the function that calculates estimate cost of upgrades
def _get_upgr_cost(cost_map, ucost, changes):
    costs = []
    for c in ast.literal_eval(str(changes)):
        try:
            costs.append(ucost[ucost['upgrade'] == c]['cost'].iloc[0])
        except:
            costs.append(0)
    return cost_map[int(max(costs))]


def add_upgrade_cost(df, ucost, first=False):
    cost_map = {0: "N/A",
                1: 'low',
                2: 'low/med',
                3: 'medium',
                4: 'med/high',
                5: 'high'}
    df['changes_cost'] = df['changes'][0 if first else 1:].apply(lambda x: _get_upgr_cost(cost_map, ucost, x))


def calc_ref_cost(orig, ref_rating, cost_w_ers):
    orig_cpy = orig.copy()
    orig_cpy['ERS Rating'] = ref_rating
    return predict_df(orig_cpy, cost_w_ers)['predicted'].iloc[0]


all_vals = [*values.heat_pumps,
            *values.heating_support,
            *values.building_env,
            *values.water_heating,
            *values.other_heat_system,
            *values.energy_prod]
