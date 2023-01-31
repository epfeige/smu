import csv
import json


def row_to_csv_file(row, header, row_num, keys):
    # create a list of values to include in the csv file
    values = [row_num]
    for i, value in enumerate(row):
        if header[i] in keys:
            values.append(value)

    # create a filename for the csv file using the row number
    filename = '{}_{}.csv'.format(row_num, 'row')

    # write the values to a csv file
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        # write the header row
        writer.writerow(keys)
        # write the row
        writer.writerow(values)


# prompt the user to enter the location and filename of the csv file
filepath = input("Enter the location and filename of the CSV file: ")

# prompt the user to enter a row number or range of rows
rows = input("Enter row number(s) or range of rows (e.g. 2, 50, 310 or 3-5): ")

# parse the input to extract the row numbers
if '-' in rows:
    # input is a range of rows
    start, end = rows.split('-')
    start = int(start)
    end = int(end)
else:
    # input is a single row or a list of rows
    row_numbers = list(map(int, rows.split(',')))

# open the csv file
with open(filepath, 'r') as f:
    # create a csv reader object
    reader = csv.reader(f)

    # get the header row
    header = next(reader)

    # load the keys from the keys.json file
    with open('keys.json', 'r') as f:
        keys = json.load(f)

    # iterate through the rows of the file
    for i, row in enumerate(reader):
        if '-' in rows:
            # input is a range of rows
            if i < start - 2 or i > end - 2:  # modified from -1 to -2 to account for header
                continue
        else:
            # input is a single row or a list of rows that are not in sequence
            if i + 2 not in row_numbers:
                continue

        # convert the row to a csv file
        row_to_csv_file(row, header, i + 2, keys)  # modified from -1 to -2 to account for header


