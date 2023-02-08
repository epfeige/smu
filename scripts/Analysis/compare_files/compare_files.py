import pandas as pd

file_1 = '../../../data/0-Original_NRCan_data/nrcan-NS-org-selected-columns-Existing-Homes-nozero.csv'
file_2 = '../../../data/0-Original_NRCan_data/nrcan-NS-org-cleanData46variables .csv'

df1 = pd.read_csv(file_1)
df2 = pd.read_csv(file_2)


# Combine the two dataframes and identify the unique rows
df_unique = pd.concat([df1, df2]).drop_duplicates(keep=False)

# Identify the unique rows in file1
df_unique_1 = df_unique[df_unique.isin(df1)].dropna()

# Identify the unique rows in file2
df_unique_2 = df_unique[df_unique.isin(df2)].dropna()

# Write a report about the comparison results to a text file
with open('compare_report.txt', 'w') as f:
    f.write('Number of rows compared: ' + str(len(df1) + len(df2)) + '\n')
    f.write('Number of rows in file 1: ' + str(len(df1)) + '\n')
    f.write('Number of rows in file 2: ' + str(len(df2)) + '\n')
    if set(df1.columns) != set(df2.columns):
        f.write('Difference in columns: ' + str(set(df1.columns) ^ set(df2.columns)) + '\n')
    else:
        f.write('No difference in columns.\n')
    f.write('Number of unique rows: ' + str(len(df_unique)) + '\n')
    f.write('Number of unique rows in file 1: ' + str(len(df_unique_1)) + '\n')
    f.write('Number of unique rows in file 2: ' + str(len(df_unique_2)) + '\n')

# Save the unique rows in file1 to a new file
df_unique_1.to_csv('unique_rows_file1.csv', index=False)

# Save the unique rows in file2 to a new file
df_unique_2.to_csv('unique_rows_file2.csv', index=False)
