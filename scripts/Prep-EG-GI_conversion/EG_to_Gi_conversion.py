import argparse
import os
import EG_to_GI_functions as EGtoGI

"""This file is to import the data from the NRCan file, run the required ERS attributes through the 
appropriate functions to get the equivalent GreenIndex (GI) value that simulates input from the agent.  
Usage: 
python3 EG_to_GI_conversion.py -f input_file.csv -o output_folder """

# --------------------------------------- Get data  (input) ---------------------------------------


# Parser for input file and output folder
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=str, required=True, help="input file")
parser.add_argument("-o", "--output", type=str, required=True, help="output folder name")

# Get arguments from command line
args = parser.parse_args()
fname_in = args.file
output_folder = args.output

# Ensure output folder exists and add '/' to end of folder name if needed
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
if output_folder[len(output_folder) - 1] != '/':
    output_folder = output_folder + '/'

# Get base name for output file
basename = os.path.splitext(os.path.basename(fname_in))[0]

# Read input data into a pandas dataframe
eg_df = EGtoGI.get_data(fname_in)

# --------------------------------------- Create GI DataFrame for output ---------------------------------------

gi_df = EGtoGI.create_GI_dataframe()

# --------------------------------------- Set GI Values & Points DataFrame (Max Points) -------------------------------

file_values = 'GI_Weights_&_Points.csv'

gi_vp = EGtoGI.get_gi_values(file_values)
gi_vp.set_index('type', inplace=True)

max_pts_ep = float(gi_vp.loc['std_points', 'Energy Efficiency'])
max_pts_ee = float(gi_vp.loc['std_points', 'Energy Production'])
max_pts_ee_ep = max_pts_ep + max_pts_ee
# --------------------------------------- Convert EG to GI and Write to DataFrame -------------------------------------

for row in eg_df.itertuples():
    index = row.Index
    # # Testing
    # if index == 10:
    #     break
    # --- ERS values from NRCan data: ----------------------

    # Following are direct/semi-direct conversions and need no function to convert to GI
    # Output column names are defined in create_GI_dataframe()
    unique_num = eg_df['unique_num'][index]  # New unique ID added to NRCan files by Peter for aligning data
    date = eg_df['CREATIONDATE'][index]  # CREATIONDATE to Date
    idnum = eg_df['IDNUMBER'][index]  # IDNUMBER to ID
    fnum = eg_df['EVAL_ID'][index]  # EVAL_ID to File number:
    prov = eg_df['PROVINCE'][index]  # PROVINCE to Province:
    post = eg_df['POSTALCODE'][index]  # POSTALCODE to Postal Code
    flom2 = round(eg_df['FLOORAREA'][index], 2)  # FLOORAREA to Living area (m2)
    floft2 = round(flom2 * 10.7639, 2)  # FLOORAREA to Living area (ft2)
    year = eg_df['YEARBUILT'][index]  # YEARBUILT to Year built
    htype = eg_df['TYPEOFHOUSE'][index]  # TYPEOFHOUSE to House Type
    stors = eg_df['STOREYS'][index]  # STOREYS to 'Stories'
    furnacefuel = str(eg_df['FURNACEFUEL'][index])  # str value of FURNACEFUEL
    wood_fuels = ('Wood Pellets', 'Softwood', 'Mixed Wood', 'Hardwood')
    if furnacefuel in wood_fuels:
        furnacefuel = 'Wood'

    haream2 = round(eg_df['HEATEDFLOORAREA'][index], 2)  # HEATEDFLOORAREA to heated area (m2)
    tothcost = round(eg_df['EGHFCOSTTOTAL'][index], 0)  # Total Heating Cost
    heatcostm2 = round(tothcost / haream2, 1)
    numwin = eg_df['NUMWINDOWS'][index]  # NUMWINDOWS to # of Windows
    numdoor = eg_df['NUMDOORS'][index]  # NUMDOORS to # of Doors
    wh_hp = str(eg_df['DHWHPTYPE'][index])  # DHWHPTYPE to existing heat pump type

    ersrating = eg_df['ERSRATING'][index]  # ERSRATING to ERS Rating
    refrating = eg_df['ERSREFHOUSERATING'][index]  # ERSREFHOUSERATING to Ref Rating
    ers_m2 = round(ersrating / haream2, 2)
    diff = round((ersrating / refrating) - 1, 1)
    diffGJ = round(ersrating - refrating, 0)
    shape = eg_df['PLANSHAPE'][index]

    # Following are for more complex conversions and are used in functions
    air50p = round(eg_df['AIR50P'][index], 2)
    actype = str(eg_df['AIRCONDTYPE'][index])  # str value from ACTYPE ("Conventional A/C", "Mini-split ductless")
    furn_type = str(eg_df['FURNACETYPE'][index])  # str value of FURNACETYPE
    hpsource = str(eg_df['HPSOURCE'][index])  # str value of HPSOURCE
    supphtgfuel1 = str(eg_df['SUPPHTGFUEL1'][index])  # str value of SUPPHTGFUEL1
    supphgttype1 = str(eg_df['SUPPHTGTYPE1'][index])  # str value of SUPPHTGTYPE1
    spaceen = eg_df['EGHSPACEENERGY'][index]  # float of EGHSPACEENERGY (Total space heating energy)
    heatenm2 = round(spaceen / haream2, 2)  # float of EGHSPACEENERGY / m2
    conse = eg_df['EGHHEATFCONSE'][index]  # float of EGHHEATFCONSE (Space energy electric)
    consg = eg_df['EGHHEATFCONSG'][index]  # float of
    conso = eg_df['EGHHEATFCONSO'][index]  # float of
    consp = eg_df['EGHHEATFCONSP'][index]  # float of
    consw = eg_df['EGHHEATFCONSW'][index]  # float of EGHHEATFCONSW (Space energy wood)
    ceilins = eg_df['CEILINS'][index]
    mainins = eg_df['MAINWALLINS'][index]  # float value from MAINWALLINS
    foundins = eg_df['FNDWALLINS'][index]  # float value from FNDWALLINS
    winestar = eg_df['NUMWINESTAR'][index]  # int from NUMWINESTAR
    doorestar = eg_df['NUMDOORESTAR'][index]  # int from NUMDOORESTAR
    eg_hrv = eg_df['CENVENTSYSTYPE'][index]  # str from CENVENTSYSTYPE
    thermos = eg_df['NELECTHERMOS'][index]  # NELECTHERMOS to # of Programable Thermostats
    solarpv = eg_df['ERSRENEWABLEELEC'][index]  # ERSRENEWABLEELEC to # of PV solar pannels - conversion of MJ to KWh
    solarhw = eg_df['NUMSOLSYS'][index]  # NUMSOLSYS to # of HW solar pannels
    dhw_hr_l1 = eg_df['DWHRL1M'][index]  # Domestic hot water heat recovery L1M
    dhw_hr_m1 = eg_df['DWHRM1M'][index]  # Domestic hot water heat recovery M1M

    print("\n------------------------------------- " + str(index) + " - " + str(fnum))
    # Group ----------------------------------------- Building Envelope -------------------------------------------

    # ---> Calculate Total for Subgroup Insulation - Attic/Ceiling *** ----
    pts_insatt = EGtoGI.insulation(ceilins, float(gi_vp.loc['std_points', 'Insulation - Attic/Ceiling']), 'attic')

    # ---> Calculate Total for Subgroup  Subgroup Insulation - Exterior Walls *** ----
    pts_insmain = EGtoGI.insulation(mainins, float(gi_vp.loc['std_points', 'Insulation - Exterior Walls']), 'main')

    # ---> Calculate Total for Subgroup  Subgroup Insulation - Foundation *** ----
    pts_insfound = EGtoGI.insulation(foundins, float(gi_vp.loc['std_points', 'Insulation - Foundation']), 'foundation')

    # ---> Calculate Total for Subgroup Windows *** ----
    pts_totwin = round((winestar / numwin) * float(gi_vp.loc['std_points', 'Windows']), 2)

    # ---> Calculate Total for Subgroup Doors *** ----
    pts_totdr = round((doorestar / numdoor) * float(gi_vp.loc['std_points', 'Doors']), 2)

    # ---> Calculate Total for Subgroup Building Airtightness *** ----
    pts_airtight = EGtoGI.draft(air50p, float(gi_vp.loc['std_points', 'Building Airtightness']))

    # -> Calculate Total for Group - Building Envelope -----------------------
    pts_max_be = float(gi_vp.loc['std_points', 'Building Envelope'])
    tot_be_pts = EGtoGI.tot_be(pts_insatt, pts_insmain, pts_insfound, pts_airtight, pts_totwin, pts_totdr, pts_max_be)
    tot_be_perc = round(tot_be_pts / float(gi_vp.loc['std_points', 'Building Envelope']), 3)  # BE in %

    # Group ----------------------------------------- Heating & Cooling ------------------------------------
    # Percentage of usage of each fuel type
    consx = round(spaceen - conse, 1)  # MJ of heating energy used other than electricity
    fuel_args = [('Wood', round(consw / spaceen, 2), consx),
                 ('Natural Gas', round(consg / spaceen, 2), consx),
                 ('Oil', round(conso / spaceen, 2), consx),
                 ('Propane', round(consp / spaceen, 2), consx),
                 ('Electricity', round(conse / spaceen, 2), conse)]
    # Find biggest percentage of fuel used
    main_fuel = max(fuel_args, key=lambda x: x[1])  # ('fuel type', % use in decimal, consx)

    # # Testing for fuel type
    #     if diff < 0.9:
    #         continue

    # ---------- Subgroup Heating System ----------

    # *** Get Heat Pump Values ***
    pts_hpmini = pts_hpair = pts_hpgeo = ['', 0, 0]  # default

    if hpsource != "N/A {no Heat Pump}":
        if actype == "Mini-split ductless":
            pts_hpmini = EGtoGI.hp_mini('Mini', actype, hpsource, main_fuel, supphgttype1, heatenm2,
                                        float(gi_vp.loc['std_points', 'Heat Pump - Mini Split']))
            # EGtoGI.print_stuff(main_fuel[0], main_fuel[1], pts_hpmini)
        elif hpsource == "Air":
            pts_hpair = EGtoGI.hp_geo_air('Air', actype, hpsource, main_fuel,
                                          float(gi_vp.loc['alt_points', 'Heat Pump - Air to air']))
        elif hpsource == "Ground" or hpsource == "Water":
            pts_hpgeo = EGtoGI.hp_geo_air('Geo', actype, hpsource, main_fuel,
                                          float(gi_vp.loc['alt_points', 'Heat Pump - Geothermal']))

    # *** Get HE Fireplace and/or Stoves and HE Pellet Stove ***
    he_ws_list = ('Advanced airtight wood stove', 'Fireplace with pilot (sealed)',
                  'Fireplace with spark ignit. (sealed)', 'Wood fireplace insert', 'Fireplace insert (EPA/CSA)',
                  'Adv. airtight wood stove + cat. conv.', 'Pellet Stove', 'Pellet stove')
    pts_he_ps = pts_he_ws = [0, 0]  # default [%, pts]
    if furn_type in he_ws_list:
        woodheat = furn_type
    elif supphgttype1 in he_ws_list:
        woodheat = supphgttype1
    else:
        woodheat = 'no'
    if woodheat != 'no':
        if woodheat == 'Pellet Stove' or woodheat == 'Pellet stove':
            pts_he_ps = EGtoGI.he_fp_ws(woodheat, consw, spaceen,
                                        float(gi_vp.loc['alt_points', 'High Efficient Woodstove or Fireplace']))
        else:
            pts_he_ws = EGtoGI.he_fp_ws(woodheat, consw, spaceen,
                                        float(gi_vp.loc['alt_points', 'High Efficient Woodstove or Fireplace']))

    # *** Get HRV Values ***
    pts_hrv = EGtoGI.hrv(eg_hrv, float(gi_vp.loc['std_points', 'Heat Recovery Ventilation (HRV)']))

    # *** Get HE furnace ***
    hp_type_used = max(pts_hpmini, pts_hpair, pts_hpgeo, key=lambda x: x[1])  # Variables contain [Name, GI %, GI pts]
    hs_subtotal = pts_hpair[2] + pts_hpgeo[2] + pts_hpmini[2] + pts_he_ps[1] + pts_he_ws[1] + pts_hrv
    hs_max_pts = float(gi_vp.loc['std_points', 'Heating System'])
    if hs_subtotal < hs_max_pts and furn_type not in he_ws_list:  # Max points for Heating system not yet reached
        if tot_be_pts < pts_max_be * 0.75 and diff <= 0.3 and hp_type_used[1] < 1:
            pts_he_furn = EGtoGI.he_furn(tot_be_pts, pts_max_be, main_fuel, heatenm2,
                                         float(gi_vp.loc['alt_points', 'High Efficient Furnace']), diff, conse, consx,
                                         haream2, *hp_type_used)
        else:
            pts_he_furn = [0, 0]
    else:
        pts_he_furn = [0, 0]

    # *** Determining if Heating System is efficient ***
    he_hsys = max(pts_he_furn[0], pts_he_ws[0], pts_he_ps[0], hp_type_used[1])
    if he_hsys < 0.2:
        no_he_sys = EGtoGI.no_he_sys(main_fuel, he_hsys)
    else:
        no_he_sys = 0

    # ---> Calculate Total Subgroup Supporting Features ----------

    # *** Get Programmable Thermostat Value
    # Note: Since this is the only feature in Supporting features, we set this to Total Supporting Features ***
    pts_thm = EGtoGI.thermostat(thermos, float(gi_vp.loc['std_points', 'Smart Thermostats']))
    pts_tot_subf = pts_thm
    sub_sfeatures_tot = min(pts_tot_subf, float(gi_vp.loc['std_points', 'Supporting Features']))  # '<= max points'

    # ---> Calculate Total for Subgroup Heating System ----------
    max_pts_hs = float(gi_vp.loc['std_points', 'Heating System'])
    max_b_pts_hs = float(gi_vp.loc['b_points', 'Heating System'])

    sub_hsys_tot = EGtoGI.tot_heatsys(max_pts_hs, no_he_sys, pts_hpmini[2], pts_hpair[2], pts_hpgeo[2], pts_hrv,
                                      pts_he_furn[1], pts_he_ps[1],
                                      sub_sfeatures_tot, pts_he_ws[1])

    # -> Calculate Total for Group - Heating & Cooling -------------
    """ We ignore AC here - since HP would only get extra points and we do not consider Window-shakers"""
    sub_ac_tot = 0
    tot_heat_n_cool = sub_hsys_tot + sub_ac_tot
    tot_hnc_perc = round(tot_heat_n_cool / float(gi_vp.loc['std_points', 'Heating & Cooling']), 3)  # H&C in %

    # Group ----------------------------------------- Water Heating -----------------------

    # *** Get value for feature dometic hot water heat pump  ***
    wh_hp_args = ('Integrated heat pump', 'Heat pump')
    if wh_hp in wh_hp_args:
        pts_dhw_sys = 1 * float(gi_vp.loc['std_points', 'Heat Pump Water Heater'])  # feature Heat Pump Water Heater
    else:
        pts_dhw_sys = 0

    # Calculate total for subgroup 'Water Heater'
    sub_w_heat_tot = min(pts_dhw_sys, float(
        gi_vp.loc['std_points', 'Water Heater']))  # Makes sure it's not above max points for subgroup

    # *** Calculate Subgroup 'Heat Recovery' points ***
    if dhw_hr_l1 == 1:
        pts_dhw_hr = 1 * float(gi_vp.loc['alt_points', 'Drain-water heat recovery < 1m'])  # Feature 1
    elif dhw_hr_m1 == 1:
        pts_dhw_hr = 1 * float(gi_vp.loc['std_points', 'Drain-water heat recovery > 1m'])  # Feature 2
    else:
        pts_dhw_hr = 0

    sub_whr_tot = min(pts_dhw_hr, float(gi_vp.loc['std_points', 'Heat Recovery']))

    # -> Calculate Total for Group - Water Heating -------------
    tot_dhw = min((sub_whr_tot + pts_dhw_sys), float(gi_vp.loc['std_points', 'Water Heating']))
    tot_dhw_perc = round(tot_dhw / float(gi_vp.loc['std_points', 'Water Heating']), 3)

    # Category ----------------------------------------- Energy Efficiency -----------------------
    total_ee = max(round(tot_heat_n_cool + tot_dhw + tot_be_pts, 2), 0)
    tot_ee_perc = round(total_ee / max_pts_ep, 2)

    # Category/Group ----------------------------------- Energy Production -----------------------

    # ---> Calculate Energy Production
    pts_spv = EGtoGI.solar_pv(solarpv, float(gi_vp.loc['std_points', 'Solar PV']))

    # ---> Calculate Solar Hot Water System
    pts_shw = EGtoGI.solar_hw(solarhw, float(gi_vp.loc['std_points', 'Solar Hot Water System']))

    # -> Calculate Total for Group - Energy Production -----------------------
    total_ep = round(pts_spv + pts_shw, 2)
    tot_ep_perc = round(total_ep / max_pts_ee, 2)

    # Category together ---------------------------------------------------------------------------
    total_ee_ep = round(total_ep + total_ee, 2)
    tot_epee_perc = round(total_ee_ep / max_pts_ee_ep, 2)

    # --------------------------------------- Add data to GI DataFrame -----------------------------------
    gi_df = gi_df.append(
        {"unique_num": unique_num, "Date": date, "ID": idnum, "EVAL_ID:": fnum, "Province": prov, "Postal Code": post,
         "Living area (ft2)": floft2, "Living area (m2)": flom2,
         "Year built": year, "House Type": htype, "Stories": stors, "Shape": shape,
         "Main Heating Fuel": furnacefuel, "heated area (m2)": haream2,
         "Total Heating Cost": tothcost, "Total Heat. Cost / m2": heatcostm2,
         "# of Doors": numdoor, "# of Windows": numwin, "SG Airtightness": pts_airtight,
         "Heat Pump - Geothermal": pts_hpgeo[2], "Heat Pump - Air to air": pts_hpair[2],
         "Heat Pump - Air to water": 0, "Heat Pump - Mini Split": pts_hpmini[2],
         'High Efficient Furnace': pts_he_furn[1], "HRV": pts_hrv,
         "High Efficiency Pellet Stove": pts_he_ps[1], "High Efficient Woodstove or Fireplace": pts_he_ws[1],
         "SG Supporting Features": pts_tot_subf, "No Primary Efficient System": no_he_sys,
         "SG Heating System": sub_hsys_tot,
         "Total Heating & Cooling": tot_heat_n_cool, "Total Heating & Cooling %": tot_hnc_perc,
         "SG Water Heater": sub_w_heat_tot,
         "SG Heat Recovery": sub_whr_tot, "Total Water Heating": tot_dhw, "Total WH %": tot_dhw_perc,
         "SG Insulation - Attic/Ceiling": pts_insatt,
         "SG Insulation - Exterior Walls": pts_insmain, "SG Insulation - Foundation": pts_insfound,
         "SG Doors": pts_totdr, "SG Windows": pts_totwin, "Total Building Envelope": tot_be_pts,
         "Total Building Envelope %": tot_be_perc,
         "Total Energy Efficiency (EE)": total_ee, "Total EE %": tot_ee_perc,
         "Solar PV": pts_spv, "Solar Hot Water System": pts_shw,
         "Total Energy Production": total_ep, "Total EP %": tot_ep_perc,
         "Combined EE & EP": total_ee_ep, "Combined EE & EP %": tot_epee_perc,
         "ERS Rating": ersrating, "Ref Rating": refrating,
         "diff %": diff, "diffGJ": diffGJ, "ERS Rating / m2": ers_m2}, ignore_index=True)
    # Ensure that unique_num is saved as int, not float
    gi_df['unique_num'] = gi_df['unique_num'].astype(int)

    # --------------------------------------- For Testing Only ---------------------------------------

    """ For Testing: """

    # Building Envelope
    be = [['attic', str(pts_insatt)], [' | main walls', str(pts_insmain)], [' | Foundation', str(pts_insfound)],
          [' | Airtight', str(pts_airtight)], [' | Total', str(tot_be_pts)], ['| Max BE:', str(pts_max_be)]]

    draft = [['Air50p |', str(air50p)], ['GI value |', 'see args'], [' Airtight |', str(pts_airtight)],
             [' Max. |', '8.46']]

    # Heating system
    hs = [['Woodheat', str(woodheat)], ['HE Fireplace', str(pts_he_ws[1])], [' | HE Pellet', str(pts_he_ps[1])],
          [' | HE Furn', str(pts_he_furn[1])],
          ['| Max HS:', str(max_pts_hs)]]

    # Main heat and heat fuel
    main_h_1 = [['main_fuel |', str(main_fuel[0:2])], ['  FFuel |', str(furnacefuel)[0:15]],
                ['  FType |', str(furn_type)[0:15]], ['  HP |', str(hp_type_used[0:15])]]

    main_h_2 = [['Pellet |', str(pts_he_ps[0])[0:15]], ['WS |', str(pts_he_ws[0])[0:15]],
                ['HE furn |', str(pts_he_furn)[0:15]]]

    heat_pump = [['HP type: ', str(hp_type_used[0])], ['HP %: ', str(hp_type_used[1])],
                 ['HP pts: ', str(hp_type_used[2])], ['Mini Split: ', str(pts_hpmini[2])]]

    # HE furnace
    # test_data = [['Diff |', str(diff)[0:10]], ['heatenm2 |', str(heatenm2)[0:13]], ['args_m2 |', str(args_m2)[0:13]],
    #              ['tot_be_pts |', str(pts_tot_be)[0:13]], ['args_be |', str(args_be)[0:13]], ['he_furn |', str(he_furn)[0:13]]]

    # EGtoGI.print_stuff(*hs)
    # EGtoGI.print_stuff(*main_h_1)
    # EGtoGI.print_stuff(*main_h_2)
    # EGtoGI.print_stuff(*heat_pump)
    # EGtoGI.print_stuff(*be)
    # EGtoGI.print_stuff(*draft)

    # print(max_pts_hs, no_he_sys, pts_hpmini[2], pts_hpair[2], pts_hpgeo[2], pts_hrv, pts_he_furn[1], pts_he_ps[1],
    #                                   sub_sfeatures_tot, pts_he_ws[1], sub_hsys_tot)

# # --------------------------------------- Write DataFrame to CSV file ---------------------------------------
# gi_df.to_csv(r'Test_GI_file.csv')
# gi_df.to_csv(r'Benchmark_test.csv')

# rearrange columns so that unique_num is first
column_names = gi_df.columns.tolist()
column_names.remove('unique_num')
column_names = ['unique_num'] + column_names
gi_df = gi_df[column_names]
gi_df.to_csv(output_folder + 'GI_' + basename + '.csv')
