import pandas as pd
import datetime

file_1 = '../../../data/0-Original_NRCan_data/nrcan-NS-org-selected-columns-Existing-Homes-nozero.csv'
file_2 = '../../../data/0-Original_NRCan_data/nrcan-NS-org-cleanData46variables.csv'

# Get the current date
now = datetime.datetime.now()

# Format the date in the desired format
current_date = now.strftime("%b. %d, %Y")

df1 = pd.read_csv(file_1)
df2 = pd.read_csv(file_2)

# Drop columns in dataframe that has extra columns to make both df identical
def drop_extra_columns(df1, df2):
    if len(df1.columns) <= len(df2.columns):
        smaller_df = df1
        larger_df = df2
    else:
        print("Warning: file2 seems to be bigger than main file. Please switch around and try again.")
        return
    smaller_df_attributes = list(smaller_df.columns)
    larger_df.drop(columns=[col for col in larger_df.columns if col not in smaller_df_attributes], inplace=True)


drop_extra_columns(df1, df2)

# Compare the two dataframes
result = df1.merge(df2, indicator=True, how='outer')
df_unique_1 = result[result['_merge'] == 'left_only']
df_unique_2 = result[result['_merge'] == 'right_only']

# Write a report about the comparison results to a text file
with open('compare_report.txt', 'w') as f:
    f.write('Comparison date: ' + current_date + '\n\n')
    f.write('File 1: (' + file_1 + ')\n')
    f.write('File 2: (' + file_2 + ')\n\n')
    f.write('Number of rows compared: ' + str(len(df1) + len(df2)) + '\n')
    f.write('Number of rows in file 1: ' + str(len(df1)) + '\n')
    f.write('Number of rows in file 2: ' + str(len(df2)) + '\n\n')
    if set(df1.columns) != set(df2.columns):
        f.write('Difference in columns: ' + str(set(df1.columns) ^ set(df2.columns)) + '\n\n')
    else:
        f.write('No difference in columns.\n\n')
    f.write('Number of unique rows: ' + str(len(df_unique_1) + len(df_unique_2)) + '\n')
    f.write('Number of unique rows in file 1: ' + str(len(df_unique_1)) + '\n')
    f.write('Number of unique rows in file 2: ' + str(len(df_unique_2)) + '\n')

# Save the unique rows in file1 to a new file
df_unique_1.to_csv('unique_rows_file1.csv', index=False)

# Save the unique rows in file2 to a new file
df_unique_2.to_csv('unique_rows_file2.csv', index=False)
