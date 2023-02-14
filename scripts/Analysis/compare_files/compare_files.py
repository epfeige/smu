"""compare two large CSV files and generate a report on the differences as well as a file
containing all the rows that are not in the other file"""

import pandas as pd
import datetime
import os

file_1 = '../../nrcan_data/nrcan-NS01eh-ORIGINAL-Existing-Homes.csv'
file_2 = '../../nrcan_data/nrcan-NS01eh-org-selected-columns-nozero.csv'

# file_1 = '../../../data/0-Original_NRCan_data/nrcan-NS-org-selected-columns-Existing-Homes-nozero.csv'
# file_2 = '../../nrcan_data/nrcan-NS01eh-ORIGINAL-Existing-Homes.csv'
# file_2 = 'compare_org-vs-unique_out/unique_rows__org-vs-46.csv'

# output folder name
output_folder = 'ORIGINAL_vs_sel-col-nozero'
# Ensure output folder exists and add '/' to end of folder name if needed
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
if output_folder[len(output_folder)-1] != '/':
    output_folder = output_folder + '/'

# Get the current date
now = datetime.datetime.now()

# Format the date in the desired format
current_date = now.strftime("%b. %d, %Y")

df1 = pd.read_csv(file_1)
df2 = pd.read_csv(file_2)


# Ensure that both df have identical columns and in the same order
def align_df_columns(df1, df2, unique_id):
    colnum_df1 = len(df1.columns)
    colnum_df2 = len(df2.columns)

    # Add unique_id column to dataframe that doesn't have it, if necessary
    if unique_id in df1.columns and unique_id not in df2.columns:
        df2[unique_id] = None
    elif unique_id in df2.columns and unique_id not in df1.columns:
        df1[unique_id] = None

    # Determine common columns and drop any that aren't common
    common_cols = set(df1.columns) & set(df2.columns)
    if unique_id in common_cols:
        common_cols.remove(unique_id)
    common_cols = sorted(list(common_cols))
    col_drop = list(set(df1.columns) - set(common_cols))
    if unique_id in col_drop:
        col_drop.remove(unique_id)

    df1_filtered = df1[common_cols]
    df2_filtered = df2[common_cols]

    # Identify rows that are different
    df_diff = pd.concat([df1_filtered, df2_filtered]).drop_duplicates(keep=False)

    # Add unique_id column back to the filtered dataframes and the diff dataframe
    if unique_id in df1.columns and unique_id in common_cols:
        df1_filtered = df1_filtered.merge(df1[[unique_id]], left_index=True, right_index=True)
        df2_filtered = df2_filtered.merge(df2[[unique_id]], left_index=True, right_index=True)
        df_diff = df_diff.merge(pd.concat([df1[[unique_id]], df2[[unique_id]]]), on=common_cols, how='outer')

    return df1_filtered, df2_filtered, colnum_df1, colnum_df2, col_drop, df_diff



# call align_df_columns
unique_id = 'unique_num'
# df1, df2, colnum_df1, colnum_df2, col_drop = align_df_columns(df1, df2, unique_id)
df1, df2, colnum_df1, colnum_df2, col_drop, df_diff = align_df_columns(df1, df2, unique_id)
df_diff.to_csv(output_folder + 'diff_rows.csv')

# Replace NaN with 0s
df1.fillna(0, inplace=True)
df2.fillna(0, inplace=True)

# print(df1.head())
# print(df2.head())

# Compare the two dataframes
result = df1.merge(df2, indicator=True, how='outer')
df_unique_1 = result[result['_merge'] == 'left_only']
df_unique_2 = result[result['_merge'] == 'right_only']

# Write a report about the comparison results to a text file
with open(output_folder + 'compare_report.txt', 'w') as f:
    f.write('Comparison date: ' + current_date + '\n\n')
    f.write('File 1: (' + file_1 + ')\n')
    f.write('File 2: (' + file_2 + ')\n\n')
    f.write('Number of rows compared: ' + str(len(df1) + len(df2)) + '\n')
    f.write('Number of rows in file 1: ' + str(len(df1)) + '\n')
    f.write('Number of rows in file 2: ' + str(len(df2)) + '\n\n')
    f.write('Number of unique rows: ' + str(len(df_unique_1) + len(df_unique_2)) + '\n')
    f.write('Number of unique rows in file 1: ' + str(len(df_unique_1)) + '\n')
    f.write('Number of unique rows in file 2: ' + str(len(df_unique_2)) + '\n\n')
    if colnum_df1 != colnum_df2:
        f.write('Difference in columns: ' + str(colnum_df1 - colnum_df2) + '\n\n')
        f.write('Columns dropped: \n\n' + str(col_drop) + '\n')
    else:
        f.write('No difference in columns.\n\n')


# Save the unique rows in file1 to a new file
df_unique_1.to_csv(output_folder + 'unique_rows_file1.csv', index=False)

# Save the unique rows in file2 to a new file
df_unique_2.to_csv(output_folder + 'unique_rows_file2.csv', index=False)
