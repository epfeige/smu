# CSV Pre_remove_nan script

## Description

This script is a Python program that uses the Pandas library to process a large CSV file. The script contains two
functions:

1. The first function takes a CSV file as input, and reads it into a pandas dataframe. It then counts the original
   number
   of rows in the file and assigns it to the variable org_row_count. It also counts the number of rows where the 'ERS
   Rating' column has a value of 0 and assigns it to the variable zero_count. Additionally, it counts the number of rows
   where the 'ERS Rating' column is empty or has a NaN value and assigns it to the variable no_value. Finally, it
   creates
   an output file that contains the following information: the name of the input file, the total number of rows, the
   number
   of rows where 'ERS Rating' is 0, and the number of rows where 'ERS Rating' has no value.
2. The second function takes the same CSV file as input and removes all the rows where the 'ERS Rating' column is 0 or
   NaN.
   It then creates a new file with _no_nan added to the original file name and writes the modified dataframe to this new
   file.
   How to run
   The script can be run by using the command:

### python

Command:
python3 pre_remove_nan.py your_file.csv
where your_file.csv is the name of the input file that the user wants to process.

## Dependencies

pandas
Please make sure that you have the above package installed in your system before running the script.

### Note
none