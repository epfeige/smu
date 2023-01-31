from flask import Flask, Blueprint, render_template, request, redirect, send_file
import csv
import json
import pandas as pd
import requests
import os
import subprocess

app = Flask(__name__)

app1_blueprint = Blueprint('app1', __name__)
app2_blueprint = Blueprint('app2', __name__)


app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['DOWNLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'json'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def predict_ers(input_file, output_file):
    # Read the input CSV file using Pandas
    df = pd.read_csv(input_file)

    # Convert the dataframe to a JSON-style dictionary
    json_data = df.to_dict(orient='records')

    # Run the prediction script for each row
    for i in range(len(json_data)):
        response = requests.post("http://md1.cs.dal.ca:3139/ers", json=json_data[i])
        json_data[i]['ER_pred'] = response.json()['result']

    # Write the new CSV file with the added column
    df = pd.DataFrame.from_dict(json_data)
    df.to_csv(output_file, index=False)


@app1_blueprint.route("/app1", methods=["GET", "POST"])
def app1_route():
    if request.method == "POST":
        input_file = request.files["inputFile"]
        output_file = request.form["outputFile"]
        predict_ers(input_file, output_file)
    return render_template("../web_multi/templates/multi.html")


@app2_blueprint.route('/app2')
def index():
    return render_template('web-ui.html')


@app2_blueprint.route('/app2/run_script', methods=['POST'])
def run_script():
    script_number = request.form['script_number']
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = file.filename
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        hostname = "ml.cs.smu.ca"
        username = "peter"
        password = "thingsWorkMonth891"
        port = 22
        script_path = os.path.dirname(os.path.abspath(__file__))
        if script_number == '1':
            if filename.rsplit('.', 1)[1] == 'json':
                with open(file_path) as json_file:
                    json_data = json.load(json_file)
                # send the json data to the specified url
                response = requests.post("http://md1.cs.dal.ca:3139/ers", json=json_data)
                # save the response in csv file
                response_data = response.json()
                csv_file_name = filename.rsplit('.', 1)[0] + '.csv'
                with open(os.path.join(app.config['DOWNLOAD_FOLDER'], csv_file_name), 'w') as f:
                    f.write(f'ers,{response_data}')
                row_id = json_data.get('first_col_value')
                ers_original = json_data.get('ER Rating')
                return render_template('web-ui.html', result=response.text, ers_org=ers_original, row=row_id)
            else:
                ssh_command = "ssh -p {} {}@{} 'cd {}; " \
                              "python3 pre.py -i models/ON_NS_ER_all.pkl -f {}'".format(port, username, hostname,
                                                                                        script_path, file_path)
                result = subprocess.check_output(ssh_command, shell=True)
                local_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], result)
                return send_file(local_file_path, as_attachment=True)

        elif script_number == '2':
            ssh_command = "ssh -p {} {}@{} 'cd {}; " \
                          "./effprop_docker.sh optimize_script.py -i {} --mec models/ON_NS_ERS_all.pkl " \
                          "--menc models/ON_NS_ERS_no_THC_no_MHF.pkl --mc models/ON_NS_Cost_all.pkl --out opt_csvs'" \
                .format(port, username, hostname, script_path, file_path)
            result = subprocess.check_output(ssh_command, shell=True)
            local_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], result)
            return send_file(local_file_path, as_attachment=True)

    else:
        return 'Invalid file'


app.register_blueprint(app1_blueprint, url_prefix='/app1')
app.register_blueprint(app2_blueprint, url_prefix='/app2')

if __name__ == "__main__":
    app.run()

