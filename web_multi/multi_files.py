from flask import Flask, render_template, request, flash, jsonify
import csv
import json
import pandas as pd
import requests
import os

app = Flask(__name__)
app.secret_key = 'Hodel3534'
output_directory = 'web_multi/output'
output_path = os.path.join(os.getcwd(), output_directory)
os.makedirs(output_path, exist_ok=True)


def predict_ers(input_file, output_file):
    df = pd.read_csv(input_file)
    df['ER_pred'] = float('nan')
    df_data = df.to_dict(orient='records')

    def get_prediction(x):
        x = json.dumps(x)
        response = requests.post("http://rnd1.cs.smu.ca:3839/ers", json=json.loads(x))
        if response.status_code != 200:
            raise ValueError(response.content)
        return response.json()
        # return response.json()['result']

    for i in range(len(df_data)):
        try:
            df_data[i].pop("ER_pred", None)
            df_data[i]['ER_pred'] = get_prediction(df_data[i])
            print(f'Processing row {i + 1} of {len(df_data)}')
        except:
            with open('output/errors.txt', 'a') as f:
                f.write(f'{i + 1}, ')
            print(f'Error on row {i + 1}')
            continue
    df = pd.DataFrame.from_records(df_data)
    print(output_path)
    df.to_csv(output_path+"/"+output_file, index=False)
    if os.path.exists(output_path + "/" + output_file):
        flash_message = 'File saved to ' + output_directory + output_file + ' with ' + output_directory + ' rows failed to process'
        return jsonify({'flash_message': flash_message})



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        input_file = request.files["inputFile"]
        output_file = request.form["outputFile"]
        folder_name = request.form['folder_name']
        predict_ers(input_file, output_file)
        if os.path.exists(output_path + "/" + output_file):
            flash_message = 'File saved to ' + folder_name + output_file
            return jsonify({'flash_message': flash_message})
        else:
            flash_message = "Error: File does not exist or there was an error checking for the file"
            return jsonify({'flash_message': flash_message})
    return render_template("multi.html")


if __name__ == "__main__":
    app.run(debug=True)
