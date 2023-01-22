# script.py
from flask import Flask, render_template, request
import csv
import json
import pandas as pd
import requests

app = Flask(__name__)


def predict_ers(input_file, output_file):
    # Read the input CSV file using Pandas
    # df = pd.read_csv(input_file)
    df = pd.read_csv(input_file, dtype={'ER_pred': float})
    df['ER_pred'] = float('nan')
    # Convert the dataframe to a JSON-style dictionary
    df_data = df.to_dict(orient='records')
    # Run the prediction script for each row
    for i in range(len(df_data)):
        # Filter data to only include the keys specified in keys.json
        # filtered_data = {k: df_data[i][k] for k in keys if k in df_data[i]}
        df_data[i].pop("ER_pred", None)
        # Write json data to file
        with open("file.json", "w") as f:
            json.dump(df_data[i], f)
        # Read json data from file
        with open("file.json", "r") as f:
            json_obj = json.load(f)
        response = requests.post("http://rnd1.cs.smu.ca:3839/ers", json=json_obj)
        result = response.text
        # df_data[i]['ER_pred'] = response.json()['result']
        #  df['ER_pred'] = df_data['ER_pred']
        df.at[i, 'ER_pred'] = result  #  df_data[i]['ER_pred']


    # Write the new CSV file with the added column
   #  df = pd.DataFrame.from_dict(df_data)
    print('outfile: ', output_file)
    df.to_csv(output_file, index=False)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        input_file = request.files["inputFile"]
        output_file = request.form["outputFile"]
        predict_ers(input_file, output_file)
    return render_template("multi.html")


if __name__ == "__main__":
    app.run(debug=True)
