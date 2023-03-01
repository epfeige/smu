import pandas as pd

# ----------------------- Get input Data ----------------------
""" this function is a simple data import for testing purposes. Unlikely to be useful for large data sets."""

def get_data(file_path):
    df = pd.read_csv(file_path, sep=',')
    return df


def get_gi_values(file_path):
    vdf = pd.read_csv(file_path, sep=',', skiprows=1)
    return vdf

# ----------------------- Group - Heating & Cooling -----------------------
# ---------- Subgroup Heating System ----------


def heat_fuel_perc(space_en, *cons):
    for i in range(len(cons)):
        perc = cons[i]/space_en
    return round(perc, 2)


# *** Heat Pump - Mini Split ***
def hp_mini(hp_type, actype, hpsource, main_fuel, supptype, heatenm2, points):
    """ Establish value for GI attribute 'Heat Pump - Mini Split' from several NRCan attributes.
        Creates 'Agent Input' first, then multiplies by related points. Considerations: How much is it used?"""
    if actype == "Mini-split ductless":
        if main_fuel[0] == "Electricity":
            if main_fuel[1] >= 0.9 and heatenm2 <= 400:
                in_hp_mini = 1
            elif main_fuel[1] >= 0.7:
                in_hp_mini = 0.8
            else:
                in_hp_mini = 0.5
        elif supptype == "N/A" and heatenm2 < 500:  # Main fuel NOT Elec. Supptype has no option for HP, hence N/A
            in_hp_mini = 0.5
        else:
            in_hp_mini = 0.25
    else:
        in_hp_mini = 0

    return [hp_type, in_hp_mini, round(in_hp_mini * points, 2)]


# *** Heat Pump - Geothermal or Heat Pump - Air to air ***
def hp_geo_air(hp_type, actype, hpsource, main_fuel, points):
    """ Establish value for GI attribute 'Heat Pump - Geothermal / Air to air' from several NRCan attributes. """
    if hpsource == "Air" or hpsource == "Ground" or hpsource == "Water":
        if main_fuel[0] == "Electricity" and main_fuel[1] >= 0.95:
            in_hp = 1
        elif main_fuel[1] >= 0.75:
            in_hp = 0.8
        elif main_fuel[1] >= 0.5:
            in_hp = 0.6
        elif main_fuel[1] >= 0.4:
            in_hp = 0.5
        else:
            in_hp = 0.25
    else:
        in_hp = 0
    return [hp_type, in_hp, round(in_hp * points, 2)]


# *** Get HE furnace ***
def he_furn(pts_tot_be, pts_max_be, main_fuel, heatenm2, points, diff, conse, consx, m2, *hp_type_used):
    args = [['Electricity', [[0.25, 250, 500], [0.5, 200, 400], [0.75, 125, 250]]],  # [Name, [BE%, SpaceEn, SpaceEn]]
            ['Wood', [[0.25, 450, 900], [0.5, 300, 600], [0.75, 250, 500]]],
            ['Oil', [[0.25, 300, 600], [0.5, 200, 400], [0.75, 200, 300]]],
            ['Propane', [[0.25, 300, 600], [0.5, 200, 400], [0.75, 200, 300]]],
            ['Natural Gas', [[0.25, 300, 600], [0.5, 200, 400], [0.75, 180, 300]]]]
    gi_val_args = (0, 1, 0.5)  # GI input Values to be assigned
    # ------------
    if hp_type_used[0] != '':  # Check if HP in use
        consx_adj = get_furncons_wo_hp(str(hp_type_used[0]), conse, consx, m2)  # Calls func. to adjust cons.
        print("HP " + str(hp_type_used[0]) + " with conse %: " + str(hp_type_used[1]))
        print("Conse: " + str(conse) + "  |  Consx: " + str(consx) + "  |  " + str(m2) + " m2  |  spaceen/m2: " + str(heatenm2))
        print("Conse/m2: " + str(round(conse / m2, 2)) + "  |  Consx/m2: " + str(round(consx / m2, 1)) + "  |  Adju.: "
              + str(consx_adj) + "\n")
        heatenm2 = consx_adj
    if main_fuel[0] == 'Wood' and main_fuel[1] < 0.98:  # wood is NOT only heat, therefore skip. Not reliable.
        return [0, 0]
    for i in range(len(args)):
        if main_fuel[0] == args[i][0]:  # Get array for matching fuel type
            prct_be_args = args[i][1]
            for k in range(len(prct_be_args)):
                if pts_tot_be < prct_be_args[k][0] * pts_max_be:  # Get array for matching level of BE
                    en_m2_args = prct_be_args[k]
                    be_val = str(pts_max_be * prct_be_args[k][0])  # Testing ---------------
                    break
            for l in range(len(en_m2_args)):
                if heatenm2 <= en_m2_args[l]:  # Get matching space energy / m2
                    gi_value = [gi_val_args[l], round(gi_val_args[l] * points * main_fuel[1], 2)]
                    break
                else:
                    gi_value = [0, 0]

    # print_HE_stuff(diff, heatenm2, str(en_m2_args[l]), pts_tot_be, be_val, gi_value)  # Testing ---------------
    return gi_value


def get_furncons_wo_hp(hp_type, conse, consx, m2):
    """Calculates (estimates) what the space energy would be without the Heat Pump. It multiplies the consumption value
    for Electricity by the efficiency ratio of the used Heat Pump."""
    args = [['Mini', 2.5], ['Air', 1.9], ['Geo', 3]]  # Heat Pump efficiency ratios
    for i in range(len(args)):
        if hp_type == args[i][0]:
            cons_furn = (conse * args[i][1]) + consx
            break
        else:
            cons_furn = consx + conse
    return round(cons_furn / m2, 1)  # return estimated consumption/m2 without the HP.


# *** HRV ***
def hrv(eg_hrv, points):
    """ Establish value for GI attribute 'Heat Recovery Ventilation (HRV)' from NRCan attribute 'CENVENTSYSTYPE' """
    if eg_hrv == "Heat recovery ventilator (HRV)" or eg_hrv == "HVI certified HRV":
        in_hrv = 1
    else:
        in_hrv = 0
    return round(in_hrv * points, 2)


# *** HE Fireplace, Stoves or Pellet stove ***
def he_fp_ws(woodheat, eghheatfconsw, eghspaceenergy, points):
    """Establish value for GI attribute 'High Efficient Woodstove or Fireplace' and Pellet Stove from NRCan data."""
    args = [['Advanced airtight wood stove', 1], ['Fireplace with pilot (sealed)', 0.95],
                  ['Fireplace with spark ignit. (sealed)', 0.95], ['Wood fireplace insert', 0.85],
                  ['Fireplace insert (EPA/CSA)', 0.85], ['Adv. airtight wood stove + cat. conv.', 1],
                  ['Pellet Stove', 1]]
    percent = eghheatfconsw / eghspaceenergy  # Estimate usage in %
    if percent < 0.25:
        per = 0
    elif percent < 0.5:
        per = 0.25
    elif percent < 0.75:
        per = 0.5
    elif percent < 1:
        per = 0.75
    else:
        per = 0.99
    for i in range(len(args)):  # loop through array (args)
        if woodheat == args[i][0]:
            gi_value = args[i][1]
            return [gi_value * per, round(gi_value * points * per, 2)]
    return [0, 0]


# *** Determining if Heating System is efficient ***
def no_he_sys(mainfuel, he_hsys):
    args = [['Electricity', -0.3], ['Oil', -0.4], ['Propane', -0.4], ['Natural Gas', -0.2], ['Wood', -0.13]]
    for i in range(len(args)):
        print("M: " + str(mainfuel[0]) + "   A: " + str(args[i][0]))
        if mainfuel[0] == args[i][0]:
            deduct = args[i][1]
            break
        else:
            deduct = 0
    print("HE max%: " + str(he_hsys) + " punish: " + str(deduct))
    return deduct



# ---------- Subgroup Supporting Features ------------
# *** Get Value for Programmable Thermostats (will also be for Subgroup Total Supporting Features ***
def thermostat(eg_value, points):
    if eg_value > 3:
        return points
    elif eg_value > 1:
        return round(0.75 * points, 2)
    elif eg_value > 0:
        return round(0.5 * points, 2)
    else:
        return 0
# ----


# *** -------------- Calculate Total for Subgroup Heating System -------------- ***
def tot_heatsys(std_points, no_he_sys, *args):  # ToDo clean up
    tot_hs_std = sum(float(i) for i in args)  # pts_hpmini + pts_hpair + pts_hpgeo + pts_hrv + pts_he_furn + pts_he_ps + pts_he_ws

    return min(round(tot_hs_std, 3), std_points)
# ----

# Group ----------------------- Building Envelope -----------------------


# *** Attic, Main and Foundation Insulation ***
def insulation(eg_value, points, area):
    """ Establish values for GI insulation attributes from NRCan attributes. """
    attic_args = [[0.38, -0.1], [2.60, 0.1], [4.60, 0.25], [8.00, 0.5], [9.00, 0.85]]  # [R-value, GI rating] Attic
    mainf_args = [[0.4, -0.1], [1.5, 0.1], [2.3, 0.25], [4, 0.5], [6, 0.80]]  # [R-value, GI rating] Mainw and Found.
    if area == 'attic':
        args = attic_args
    else:
        args = mainf_args
    for i in range(len(args)):
        if eg_value < args[i][0]:
            gi_value = args[i][1]
            return round(gi_value * points, 2)
    return 1 * points


# *** Airtightness ***
def draft(eg_value, points):
    """ Establish values for GI airtighness attribute from NRCan AIR50P data. """
    airtight_args = [[1.5, 1.0], [3.0, 0.75], [7.5, 0.5], [12.5, -0.25]]  # [AIR50P, GI rating]
    for i in range(len(airtight_args)):
        if eg_value < airtight_args[i][0]:
            gi_value = airtight_args[i][1]
            return round(gi_value * points, 2)
    return round(-0.5 * points, 2)  # For values bigger than 12.5


# *** -------------- Calculate Total Building Enevelope (Group)-------------- ***
def tot_be(pts_insatt, pts_insmain, pts_insfound, pts_drafty, pts_totw, pts_totd, max_points):
    """ Establish Total BE score. """
    total_be = round((pts_insatt + pts_insmain + pts_insfound + pts_drafty + pts_totw + pts_totd), 2)
    if total_be > max_points:
        return max_points
    else:
        return total_be


# ----------------------- Category/Group - Energy Production -----------------------
# ----------------------- Subgroup - Existing -----------------------

# *** Solar PV ***
def solar_pv(eg_value, points):
    """" Estblish Solar PV score. """
    num_5k = eg_value / 18720
    if num_5k > 3:
        return 1 * points
    elif num_5k > 1.5:
        return 0.75 * points
    elif num_5k > 0.3:
        return 0.25 * points
    else:
        return 0


# *** Solar Hot Water (Energy Production) ***
def solar_hw(eg_value, points):
    """ Establish Solar Hot Water Score"""
    if eg_value >= 2:
        return 1
    elif eg_value == 1:
        return 0.5
    else:
        return 0


# -----------------------  Write file -----------------------
def create_GI_dataframe():
    fieldnames = ['ID', 'Date', 'EVAL_ID:', 'Province', 'Postal Code', 'Living area (ft2)', 'Living area (m2)',
                  'Year built', 'House Type', 'Stories', 'Shape', 'Main Heating Fuel', 'heated area (m2)', '# of Doors',
                  '# of Windows', 'Total Heating Cost', 'Total Heat. Cost / m2', 'Heat Pump - Geothermal',
                  'Heat Pump - Air to air', 'Heat Pump - Air to water',
                  'Heat Pump - Mini Split', 'High Efficient Furnace', 'High Efficiency Pellet Stove',
                  'High Efficient Woodstove or Fireplace', 'HRV', 'SG Supporting Features',
                  'No Primary Efficient System', 'SG Heating System', 'Total Heating & Cooling',
                  'Total Heating & Cooling %',
                  'SG Insulation - Attic/Ceiling', 'SG Insulation - Exterior Walls',
                  'SG Insulation - Foundation', 'SG Doors', 'SG Windows', 'SG Airtightness',
                  'Total Building Envelope', 'Total Building Envelope %', 'SG Water Heater', 'SG Heat Recovery',
                  'Total Water Heating', 'Total WH %',
                  'Total Energy Efficiency (EE)', 'Total EE %', 'Solar PV', 'Solar Hot Water System',
                  'Total Energy Production', 'Total EP %',
                  'Combined EE & EP', 'Combined EE & EP %', 'ERS Rating',
                  'Ref Rating', 'diff %', 'diffGJ', 'ERS Rating / m2']
    return pd.DataFrame(columns=fieldnames)


def writecsv(gi_file, gi_df):
    dir_path = ""
    file_nam = gi_file
    file = "r'" + dir_path + file_nam + "'"
    gi_df.to_csv(file)


# Functions for Testing ---------------------------------

def print_HE_stuff(diff, heatenm2, args_m2, pts_tot_be, args_be, he_furn):
    test_data = [['Diff', 'heatenm2', 'args_m2', 'tot_be_pts', 'args_be', 'he_furn'],
                 [diff, heatenm2, args_m2, pts_tot_be, args_be, he_furn]
                 ]
    for row in test_data:
        print("{: >10} {: >15} {: >15} {: >15} {: >15} {: >15}".format(*row))


def print_stuff(*args):
    fieldnames = []
    for i in range(len(args[0])):
        fieldnames.append(str(args[i][0]))

    prt_df = pd.DataFrame(columns=fieldnames)
    for i in range(len(args)):
        prt_df.loc[1, args[i][0]] = args[i][1] + " "

    print(prt_df)
    print('\n')
