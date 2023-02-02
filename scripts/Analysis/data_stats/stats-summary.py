# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from prettytable import PrettyTable


# Importing the dataset
# -- parser will get the file and output folder information --
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=str, required=True, help="input file")
parser.add_argument("-o", "--output", type=str, required=True, help="output folder name")
# Parse arguments from command line ('simplified' parser command)
args = parser.parse_args()
# Access the arguments in  script
input_file = args.file
output_folder = args.output
# Ensure folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
# Add / to end of folder name
if output_folder[len(output_folder)-1] != '/':
    output_folder = output_folder + '/'
# for output file name
basename = os.path.splitext(os.path.basename(input_file))[0]
# get data from input file and put it into a pandas dataframe
data = pd.read_csv(input_file)

# Adding the two extra columns to store diffs in
data['ER-EP_diff%'] = (data['predicted'] - data['ERS Rating']) / data['ERS Rating']
data['Abs ER-EP_diff%'] = abs(data['ER-EP_diff%'])

# Creating the statistics
total_rows = len(data)
above_10 = [len(data[data['ER-EP_diff%'] > 0.1]), len(data[data['ER-EP_diff%'] > 0.1]) / total_rows]
below_10 = [len(data[data['ER-EP_diff%'] < -0.1]), len(data[data['ER-EP_diff%'] < -0.1]) / total_rows]
abs_10 = [len(data[data['Abs ER-EP_diff%'] > 0.1]), len(data[data['Abs ER-EP_diff%'] > 0.1]) / total_rows]
above_20 = [len(data[data['ER-EP_diff%'] > 0.2]), len(data[data['ER-EP_diff%'] > 0.2]) / total_rows]
below_20 = [len(data[data['ER-EP_diff%'] < -0.2]), len(data[data['ER-EP_diff%'] < -0.2]) / total_rows]
abs_20 = [len(data[data['Abs ER-EP_diff%'] > 0.2]), len(data[data['Abs ER-EP_diff%'] > 0.2]) / total_rows]
above_50 = [len(data[data['ER-EP_diff%'] > 0.5]), len(data[data['ER-EP_diff%'] > 0.5]) / total_rows]
below_50 = [len(data[data['ER-EP_diff%'] < -0.5]), len(data[data['ER-EP_diff%'] < -0.5]) / total_rows]
abs_50 = [len(data[data['Abs ER-EP_diff%'] > 0.5]), len(data[data['Abs ER-EP_diff%'] > 0.5]) / total_rows]
max_diff = max(data['ER-EP_diff%'])
min_diff = min(data['ER-EP_diff%'])
avg_diff = np.mean(data['ER-EP_diff%'])
avg_diff_without_outliers = np.mean(data[(data['ER-EP_diff%'] > -0.1) & (data['ER-EP_diff%'] < 0.1)]['ER-EP_diff%'])

# Creating a file with the outliers within 10%
dataset_within_10 = data[(data['ER-EP_diff%'] > -0.1) & (data['ER-EP_diff%'] < 0.1)]
dataset_within_10.to_csv(output_folder + basename + '_within_10%.csv', index=False)
df10 = pd.DataFrame(dataset_within_10)
# print(df10['predicted'])

# print('Max. ER-EP_diff%:', max_diff)
# print('Min. ER-EP_diff%:', min_diff)
# print('Average ER-EP_diff%:', avg_diff)
# print('Average ER-EP_diff% without outliers above or below 10%:', avg_diff_without_outliers)

# Creating output dataframe
df = pd.DataFrame({'Above 10%': above_10, 'Below 10%': below_10, 'Absolute 10%': abs_10, 'Above 20%': above_20, 'Below 20%': below_20, 'Absolute 20%': abs_20, 'Above 50%': above_50, 'Below 50%': below_50, 'Absolute 50%': abs_50}, index=['Count', 'Percentage'])


# Plot the first chart
df.plot(kind='bar', figsize=(6,3), label = "Stats")
plt.title('Statistics')
plt.xlabel('Count')
plt.ylabel('Number of rows')
plt.savefig(output_folder + "chart1.png")
plt.clf()

# Plot the second chart
df10['predicted'].plot(kind='hist', bins=100, figsize=(6, 3), label = "EP")
plt.title('EP')
plt.savefig(output_folder + "chart_EP.png")
plt.clf()

# Plot the third chart
df10['ERS Rating'].plot(kind='hist', bins=100, figsize=(6, 3), label = "ERS")
plt.title('ERS')
plt.savefig(output_folder + "chart_ERS.png")
plt.clf()


def create_statistics_table(statistics):
    table = PrettyTable()
    table.field_names = ['Key', 'Count', 'Percent']
    for key, (count, percent) in statistics:
        table.add_row([key, count, percent])
    return table

# Creating the file with the statistics
statistics = [
    ('Above 10%', above_10),
    ('Below -10%', below_10),
    ('Absolute 10%', abs_10),
    ('Above 20%', above_20),
    ('Below -20%', below_20),
    ('Absolute 20%', abs_20),
    ('Above 50%', above_50),
    ('Below -50%', below_50),
    ('Absolute 50%', abs_50)
]

table = create_statistics_table(statistics)

with open(output_folder + '_statistics.txt', 'w') as f:
    f.write('Total rows: ' + str(total_rows) + '\n')
    f.write(str(table))


# Read the data from the text file
with open(output_folder + '_statistics.txt', 'r') as f:
    data = f.readlines()

# Create the PDF document
doc = SimpleDocTemplate(output_folder + "report.pdf", pagesize=landscape(letter))
elements = []

# Add the data from the text file to the PDF
table_data = [['Keys', 'Count', 'Percent']]
for statistic in statistics:
    table_data.append([statistic[0], statistic[1][0], statistic[1][1]])
table = Table(table_data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
elements.append(table)


# Add the charts to the PDF
elements.append(Image(output_folder + "chart1.png"))
elements.append(Image(output_folder + "chart_EP.png"))
elements.append(Image(output_folder + "chart_ERS.png"))


# Build the PDF
doc.build(elements)


