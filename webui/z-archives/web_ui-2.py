import requests
from flask import Flask, render_template, request, redirect, send_from_directory
import os
import json

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run_script', methods=['POST'])
def run_script():
    script = request.form['script']
    file = request.files['file']
    file.save(file.filename)  # save the uploaded file to the server
    # result_folder = request.form['result_folder']
    result_folder = '/test'

    if script == 'ER':
        with open(file.filename, 'r') as json_file:
            json_data = json.load(json_file)

        result = requests.post("http://rnd1.cs.smu.ca:3839/ers", json=json_data)
        # return str(result)
        return render_template('index.html', result=result.text)
    elif script == 'OPTI':
        os.system(
            f'../scripts/effprop_docker.sh optimize_script.py -i {file.filename} --mec models/ON_NS_ERS_all.pkl --menc models/ON_NS_ERS_no_THC_no_MHF.pkl --mc models/ON_NS_Cost_all.pkl --out {result_folder}')
        return redirect('/download_csv')
    elif script == 'Report':
        # ----report commands----
        return redirect('/download_pdf')


@app.route('/download_csv')
def download_csv(result_folder):
    # Get the original file name
    original_file_name = request.args.get('file_name')
    # Create the output file name
    output_file_name = original_file_name.split('.')[0] + '-out.csv'
    # Specify the directory where the CSV file is located
    # Use the send_from_directory() function to send the file to the user
    return send_from_directory(result_folder, output_file_name, as_attachment=True)


@app.route('/download_pdf')
def download_pdf():
    # generate the pdf file and provide a link for the user to download it
    pass

    # app.run(host='http://ml.cs.smu.ca', port=5000, debug=False)


if __name__ == '__main__':
    app.run(debug=True)
