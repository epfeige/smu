# Flask for ERs Prediction using SMU web service

A Flask application that predicts ERS values based on a CSV input file and write a new CSV file 
with a new column for the predictions.

### Requirements
- pandas
- Flask
- requests
- CSV input file has to have specific columns. 
  It can have extra columns but not less than required column (see keys.json file)


### Usage
1. Start the Flask application by running python3 multi_files.py
2. Open the website link in a browser
3. Send a POST request to the endpoint with the input file and output file in the request data.
4. The response will render the multi.html template with the prediction results.

### Functionality

1. The application reads a CSV file using pandas.
2. A new column named 'ER_pred' with NaN values is added to the dataframe.
3. The dataframe is converted to a dictionary with the 'records' orientation.
4. The get_prediction function is defined to take in a row of the dictionary and send a post request to a specified endpoint with the row as JSON data.
5. The function returns the 'result' field of the JSON response.
6. The get_prediction function is applied to each row of the dictionary using the 'apply' method and assigns the returned value to the corresponding 'ER_pred' column of the dataframe.
7. The updated dataframe is written to a CSV file with the specified output file name and index set to False.

### File Structure

├── app.py

├── templates

│   └── multi.html

└── requirements.txt
