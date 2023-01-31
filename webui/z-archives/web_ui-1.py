from flask import Flask, request, render_template, redirect, send_file
import os
import subprocess

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'scripts/Josh/uploads'
pwd
app.config['ALLOWED_EXTENSIONS'] = {'csv'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run_script', methods=['POST'])
def run_script():
    command = request.form['command']
    script_number = request.form['script_number']
    file = request.files['file']
    hostname = "ml.cs.smu.ca"
    username = "Peter"
    password = "thingsWorkMonth891"
    port = 22
    rootpath = "home/peter"
    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if script_number == '1':
            ssh_command = "sshpass -p {} ssh -p {} {}@{} 'cd {}; " \
                          "python3 scripts/predict_script.py -i scripts/models/ON_NS_ERS_all.pkl -f {}".format(password,
                                                                                                               port,
                                                                                                               username,
                                                                                                               hostname,
                                                                                                               rootpath,
                                                                                                               filename)
        elif script_number == '2':
            ssh_command = "sshpass -p {} ssh -p {} {}@{} 'cd {}; " \
                          "scripts/./effprop_docker.sh optimize_script.py -i {} --mec scripts/models/ON_NS_ERS_all.pkl " \
                          "--menc models/ON_NS_ERS_no_THC_no_MHF.pkl --mc models/ON_NS_Cost_all.pkl --out opt_csvs".format(
                password, port, username, hostname, rootpath, filename)

        result = subprocess.check_output(ssh_command, shell=True)
        local_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return send_file(local_file_path, as_attachment=True)
    else:
        return 'Invalid file'


if __name__ == '__main__':
    app.run()
