"""
This script is a command line tool that detects outliers in specific attributes of a CSV file using the
Z-score method. It replaces any NaN values in the specified attributes with zeros, and outputs the rows that have
a Z-score greater than 3 in any of the specified attributes.

USAGE: python script.py -f in_file.csv -a attribute_file.txt
"""

import pandas as pd
import numpy as np
import argparse
import csv

# Define a function to parse the command line arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--in_file', required=True, help='Input CSV file')
    parser.add_argument('-a', '--attribute_file', required=True, help='File with list of attributes to check')
    parser.add_argument('-d', '--debug', action='store_true', help='Turn on debug output')
    return parser.parse_args()

# Define a function to check which columns in the dataframe have numerical values
def check_numeric_columns(df):
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    return numeric_columns

# Define a function to replace NaN values with 0 in the specified columns
def replace_NaNs_with_zeros(df, columns):
    df[columns] = df[columns].fillna(0)
    return df

# Define a function to detect outliers using the Z-score method
def detect_outliers(df, columns):
    outlier_rows = []
    dfstats = pd.DataFrame(columns=["Attribute", "Mean", "Std", "z-mean"])
    for column in columns:
        mean = df[column].mean()
        std = df[column].std()
        z_scores = (df[column] - mean) / std
        initial_outliers = df[z_scores.abs() > 4]
        dfstats = dfstats.append({"Attribute": column, "Mean": mean, "Std": std, "z-mean": z_scores.mean()}, ignore_index=True)
        dfstats.to_csv('dfstats.csv')
        for second_pass_column in initial_outliers.columns:
            if second_pass_column not in columns:
                continue
            print(second_pass_column)
            second_mean = dfstats[dfstats["Attribute"] == second_pass_column]["Mean"].iloc[0]
            print(second_mean)
            second_std = dfstats[dfstats["Attribute"] == second_pass_column]["Std"].iloc[0]
            second_z_scores = (initial_outliers[second_pass_column] - second_mean) / second_std
            second_pass_outliers = initial_outliers[second_z_scores.abs() > 3]
            for index, row in second_pass_outliers.iterrows():
                record_id = row["EVAL_ID"]
                attribute = second_pass_column
                zscore = second_z_scores.loc[index]
                mean_value = second_mean
                std_value = second_std
                value = row[second_pass_column]
                outlier_attribute = "outlier" if zscore > 0 else "negative outlier"
                outlier_rows.append([record_id, attribute, zscore, value, mean_value, std_value, outlier_attribute])
    return pd.DataFrame(outlier_rows, columns=["EVAL_ID", "Attribute", "Z-score", "Value", "Mean", "Std", "Outlier Attribute"])



# Define a function to print the outliers with their attribute values marked as bold
def print_outliers(outlier_rows):
    print('\033[1m' + 'Outlier rows:' + '\033[0m')
    for index, row in outlier_rows.iterrows():
        print('\033[1m' + 'Row ' + str(index) + ': ' + '\033[0m', row.to_string(index=False))


# def write_to_csv(outliers, attribute_file, output_file):
#     with open(output_file, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(["Record ID", "Attribute", "Z-score", "Value"])
#         for outlier in outliers:
#             writer.writerow([outlier[0], outlier[1], outlier[2], outlier[3]])



# Main function
def main():
    # Parse the command line arguments
    args = parse_args()

    # Read the input CSV file into a Pandas dataframe
    df = pd.read_csv(args.in_file)

    # Read the list of attributes to check for outliers
    with open(args.attribute_file) as f:
        attributes_to_check = f.read().strip().split(',')
    attributes_to_check = [attribute.strip().replace("'", "") for attribute in attributes_to_check]

    # Check which columns in the dataframe have numerical values
    numeric_columns = check_numeric_columns(df)

    if args.debug:
        print("Numeric columns:", numeric_columns)

    # Intersect the specified attributes with the numeric columns
    numeric_attributes_to_check = list(set(attributes_to_check) & set(numeric_columns))

    if args.debug:
        print("Numeric attributes to check:", numeric_attributes_to_check)

    # Replace NaN values with 0 in the specified numeric attributes
    df = replace_NaNs_with_zeros(df, numeric_attributes_to_check)

    if args.debug:
        print("Dataframe after replacing NaN with 0:", df)

    # Detect outliers in the specified numeric attributes using the Z-score method
    outlier_rows = detect_outliers(df, numeric_attributes_to_check)

    # Print the outliers with their attribute values marked as bold
    # print_outliers(outlier_rows)

    if args.debug:
        print("Outlier rows:", outlier_rows)

    if args.debug:
        print('Input dataframe shape: ', df.shape)
        print('Numeric columns in input dataframe: ', numeric_columns)
        print('Attributes to check: ', attributes_to_check)
        print('Numeric attributes to check: ', numeric_attributes_to_check)

    # Save the outlier rows to a CSV file
    outlier_rows.to_csv(args.in_file.replace('.csv', '_output.csv'), index=False)

    # write_to_csv(outlier_rows, args.attribute_file, 'outliers-z.csv')


# Call the main function if the script is being run as a standalone program
if __name__ == '__main__':
    main()
