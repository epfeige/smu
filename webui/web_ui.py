import logging

from flask import Flask, request, render_template, redirect, send_file
import os
import subprocess
import json
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['DOWNLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'json'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return render_template('web-ui.html')


@app.route('/run_script', methods=['POST'])
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
                response = requests.post("http://rnd1.cs.smu.ca:3839/ers", json=json_data)
                # save the response in csv file
                response_data = response.json()
                csv_file_name = filename.rsplit('.', 1)[0] + '.csv'
                with open(os.path.join(app.config['DOWNLOAD_FOLDER'], csv_file_name), 'w') as f:
                    f.write(f'ers,{response_data}')
                    # for key in response_data.keys():
                    #     f.write("%s,%s\n" % (key, response_data[key]))
                row_id = json_data.get('first_col_value')
                ers_original = json_data.get('ERS Rating')
                return render_template('web-ui.html', result=response.text, ers_org=ers_original, row=row_id)
                # return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], csv_file_name), as_attachment=True)
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


if __name__ == '__main__':
    app.run()
