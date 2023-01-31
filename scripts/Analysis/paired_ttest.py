from scipy.stats import ttest_rel
import pandas as pd
import re


ers = 'ERS Rating'
ep = 'ER_pred'
# Import your data into a Pandas DataFrame
df = pd.read_csv("Oil/All_Oil_Properties_With_EP.csv")


df[ers] = df[ers].replace(re.compile('[^0-9.]'), pd.np.nan)
df[ep] = df[ep].replace(re.compile('[^0-9.]'), pd.np.nan)
df.dropna(inplace=True)
df[ers] = df[ers].astype(float)
df[ep] = df[ep].astype(float)

# Extract the columns for the original and predicted values
original_values = df[ers]
predicted_values = df[ep]

# Perform the t-test
t_value, p_value = ttest_rel(original_values, predicted_values)

# Print the results
print("t-value: ", t_value)
print("p-value: ", p_value)