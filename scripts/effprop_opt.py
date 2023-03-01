import pandas as pd
import values as values


# *** this script is part of optimize_script.py ***

# ----------------------- Get Data ----------------------
def get_data(file_path):  # Doesn't seem to be used anywhere
    df = pd.read_csv(file_path, sep=',')
    return df


def get_gi_values(file_path):
    vdf = pd.read_csv(file_path, sep=',', skiprows=1)
    return vdf


def is_above(a_val, goal, perc):
    if a_val >= (goal * perc):
        return True
    else:
        return False


# ----------------------- Group - Heating & Cooling -----------------------
class Attribs:
    def __init__(self):
        self.the_list = []

    def heating_system(self, df, row, max_pts_hp, max_pts_hnc, main_fuel):
        hp_args = values.heat_pumps
        hp_tot, hs_tot = 0, 0
        hp_list, hp_all = [], []

        for i in range(len(hp_args)):
            if df.iloc[row, df.columns.get_loc(hp_args[i][0])] >= max_pts_hp:  # this HP 100% used (break)
                # print('top HP - no Heating system upgrade needed')
                hp_list, hp_all = [], []
                hp_tot = hp_tot + df.iloc[row, df.columns.get_loc(hp_args[i][0])]
                break
            elif df.iloc[row, df.columns.get_loc(hp_args[i][0])] != 0:
                hp_list.append(hp_args[i][0])  # this HP is somewhat used (add to list)
                hp_tot = hp_tot + df.iloc[row, df.columns.get_loc(hp_args[i][0])]

        if hp_tot == 0:
            hp_list = [hp_args[3][0]]

        self.the_list.extend(hp_list)
        if hp_tot < max_pts_hp:
            hs_args = values.other_heat_system
            for h in range(len(hs_args)):
                self.the_list.append(hs_args[h][0])
                hs_tot = hs_tot + df.iloc[row, df.columns.get_loc(hs_args[h][0])]
        if hs_tot < max_pts_hnc:
            sup_args = values.heating_support
            for h in range(len(sup_args)):
                if df.iloc[row, df.columns.get_loc(sup_args[h][0])] < sup_args[h][1]:
                    self.the_list.append(sup_args[h][0])
                    hs_tot = hs_tot + df.iloc[row, df.columns.get_loc(sup_args[h][0])]
        # if main_fuel != "Electric" and hp_tot <= (0.5 * max_pts_hp):
        #     the_list.append("Main Heating Fuel")
        return self.the_list

    # ----------------------- Group - other than HnC -----------------------
    def attris(self, df, row, att):
        args = att
        list = []
        for i in range(len(args)):
            if df.iloc[row, df.columns.get_loc(args[i][0])] >= args[i][1][0]:
                # print(args[i][0] + ' is sufficient')
                continue
            else:
                # print(args[i][0] + ' not sufficient')
                list.append(args[i][0])
                # print('sublist: ', list)

        self.the_list.extend(list)
        return self.the_list


"""This file is to create a list of attributes to run an application which will determine what specific attributes
 will result in the lowest GJ/year in the ML prediction"""


def get_attributes_for_upgrade(GI_values, gi_df):
    # ----- GreenIndex Max values ------
    # GI_values = 'GI_Weights_&_Points.csv'
    a = Attribs()
    gi_vp = get_gi_values(GI_values)
    gi_vp.set_index('type', inplace=True)

    max_pts_ee = float(gi_vp.loc['std_points', 'Energy Efficiency'])
    max_pts_ep = float(gi_vp.loc['std_points', 'Energy Production'])
    max_pts_be = float(gi_vp.loc['std_points', 'Building Envelope'])
    max_pts_hnc = float(gi_vp.loc['std_points', 'Heating & Cooling'])
    max_pts_hs = float(gi_vp.loc['std_points', 'Heating System'])
    max_pts_hp = float(gi_vp.loc['std_points', 'Heat Pump - Mini Split'])
    max_pts_wh = float(gi_vp.loc['std_points', 'Water Heating'])

    # --------------------------------------- Get actual data ---------------------------------------
    # fname_in = "all_cols_sample.csv"
    # gi_df = get_data(fname_in)

    row = 0
    # Which row to use from dataframe

    # Get values from specific listing to be analysed. Sometimes we need to use the points, instead of %
    postal = gi_df.iloc[row, gi_df.columns.get_loc('Postal Code')]
    area_liv = gi_df.iloc[row, gi_df.columns.get_loc('Living area (ft2)')]
    year = gi_df.iloc[row, gi_df.columns.get_loc('Year built')]
    stories = gi_df.iloc[row, gi_df.columns.get_loc('Stories')]
    main_fuel = gi_df.iloc[row, gi_df.columns.get_loc('Main Heating Fuel')]
    area_heat = gi_df.iloc[row, gi_df.columns.get_loc('heated area (m2)')]
    num_win = gi_df.iloc[row, gi_df.columns.get_loc('# of Windows')]
    tot_cost = gi_df.iloc[row, gi_df.columns.get_loc('Total Heating Cost')]
    tot_hnc_per = gi_df.iloc[row, gi_df.columns.get_loc('Total Heating & Cooling %')]
    tot_hnc = gi_df.iloc[row, gi_df.columns.get_loc('Total Heating & Cooling')]
    tot_be_per = gi_df.iloc[row, gi_df.columns.get_loc('Total Building Envelope %')]
    tot_be = gi_df.iloc[row, gi_df.columns.get_loc('Total Building Envelope')]
    tot_ee_per = gi_df.iloc[row, gi_df.columns.get_loc('Total EE %')]
    tot_ee = gi_df.iloc[row, gi_df.columns.get_loc('Total Energy Efficiency (EE)')]
    tot_ep_per = gi_df.iloc[row, gi_df.columns.get_loc('Total EP %')]
    tot_ep = gi_df.iloc[row, gi_df.columns.get_loc('Total Energy Production')]
    tot_wh = gi_df.iloc[row, gi_df.columns.get_loc('Total Water Heating')]
    hp_geo = gi_df.iloc[row, gi_df.columns.get_loc('Heat Pump - Geothermal')]
    hp_aa = gi_df.iloc[row, gi_df.columns.get_loc('Heat Pump - Air to air')]
    hp_aw = gi_df.iloc[row, gi_df.columns.get_loc('Heat Pump - Air to water')]
    hp_mini = gi_df.iloc[row, gi_df.columns.get_loc('Heat Pump - Mini Split')]
    he_furn = gi_df.iloc[row, gi_df.columns.get_loc('High Efficient Furnace')]
    he_pellet = gi_df.iloc[row, gi_df.columns.get_loc('High Efficiency Pellet Stove')]
    he_woodfire = gi_df.iloc[row, gi_df.columns.get_loc('High Efficient Woodstove or Fireplace')]
    hrv = gi_df.iloc[row, gi_df.columns.get_loc('HRV')]

    # ---------------------------------- Create empty DataFrame / list for output ----------------------------

    # ---------------------------------------  -------------------------------------

    # Test for EE threshold first and see if it is below or above. If above, no upgrades needed. Go to EP
    if is_above(tot_ee, max_pts_ee, 0.95):
        pass
        # print('EE has efficient score. No major upgrade needed. Go to EP.')
    else:
        # print('EE is below ' + str(max_pts_ee * 0.95) + '. Check groups.')
        if is_above(tot_hnc, max_pts_hnc, 1):
            pass
            # print('HnC 100% - go to next group')
        else:
            # print('HnC < 100% - ' + str(max_pts_hnc) + ' - test attributes in this group')
            attribute_list = a.heating_system(gi_df, row, max_pts_hp, max_pts_hnc, main_fuel)
            # support = Meth.
            # attribute_list.append(support)

        # Check BE
        if is_above(tot_be, max_pts_be, 1):
            pass
            # print('BE 100% - go to next group')
        else:
            # print('BE < 100% - test attributes in this group')
            att = values.building_env
            attribute_list = a.attris(gi_df, row, att)
        # Check Water Hating
        if is_above(tot_wh, max_pts_wh, 1):
            pass
            # print('WH 100% - go to next group')
        else:
            # print('WH < 100% - test attributes in this group')
            att = values.water_heating

            # print(att)
            attribute_list = a.attris(gi_df, row, att)

    # ----- Energy Production ------
    # if not is_above(tot_ep, max_pts_ep, 0.8):
    #    attep = values.energy_prod
    #    #print(attep)
    #    attribute_list = a.attris(gi_df, row, attep)

    return attribute_list
    # print('A: ', attribute_list)


# # --------------------------------------- Notes to get values for ML ---------------------------------------
'''
    'Main Heating Fuel' - I don't know yet what to do with this. It should change over to electric if only electric 
    heating and water heating is in use. 
    
    'Total Heating & Cooling %' 
    = sum of all points in that attribute list divided by Max points for Total heating & cooling 
    
    'Total Building Envelope %'
    = sum of all points in that attribute list divided by Max points for Total Building Envelop
    
    'Total EE %',
    = sum of all of the above divided by Max points EE
    
    'Total EP %'
    
'''


# Get new values from optimization -------------------------------------
def update_mhf(gi_df):
    electrical = values.heat_pumps
    wood = []
    wood.append(values.other_heat_system[1])
    wood.append(values.other_heat_system[2])

    for row in range(0, len(gi_df)):
        main_fuel = gi_df.iloc[row, gi_df.columns.get_loc('Main Heating Fuel')]

        # -------------------------------------------

        # Check if any of the Heat Pumps are used more than 50%
        for i in range(len(electrical)):
            if gi_df.iloc[row, gi_df.columns.get_loc(electrical[i][0])] > (0.5 * electrical[i][1][0]):
                main_fuel = 'Electricity'
                break

        # Check Wood/Pellet heating
        wood_max, wood_total = 0, 0
        for i in range(len(wood)):
            if gi_df.iloc[row, gi_df.columns.get_loc(wood[i][0])] > 1:
                wood_total = wood_total + gi_df.iloc[row, gi_df.columns.get_loc(wood[i][0])]
                wood_max = wood_max + wood[i][1][0]

        if wood_max > 0:
            if wood_total / wood_max > 0.5:
                main_fuel = 'Wood'

        gi_df.iloc[row, gi_df.columns.get_loc('Main Heating Fuel')] = main_fuel
