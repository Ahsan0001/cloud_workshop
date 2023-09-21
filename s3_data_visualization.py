from pathlib import Path

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import os
import json
import boto3

# AWS Credentials (you can also configure these using AWS CLI or environment variables)
AWS_ACCESS_KEY_ID = 'AKIASWMFEERTPHCGRI2Z'
AWS_SECRET_ACCESS_KEY = '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'
BUCKET_NAME = 'cloud-workshop-test-bucket'
topic = 'workshop/publish'
LOCAL_DOWNLOAD_PATH = os.getcwd() + '/s3_data'
DATA_PATH = LOCAL_DOWNLOAD_PATH + '/' + topic
print(LOCAL_DOWNLOAD_PATH)

# Initialize the S3 client
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# Sample data for plotting
x_values = [1, 2, 3, 4, 5]
y_values = [10, 11, 12, 13, 14]

# Initialize Dash App
app = dash.Dash(__name__)

# Define Layout
app.layout = html.Div([
    html.H1("Plotly Graph in Dash"),

    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Scatter', 'value': 'scatter'},
        ],
        value='option1'
    ),

    # Plotly Graph
    dcc.Graph(id='plot')
])


def get_data_from_files(folder_path):
    timestamps, temperatures, humidities, pressures = [], [], [], []

    for filename in os.listdir(folder_path):
        if '.' not in filename:  # Assuming files with no extension contain the required data
            with open(os.path.join(folder_path, filename), 'r') as file:
                data = json.loads(file.read())
                timestamps.append(data['timestamp'])
                temperatures.append(data['temperature'])
                humidities.append(data['humidity'])
                pressures.append(data['pressure'])

    return timestamps, temperatures, humidities, pressures


def fetch_files_from_s3():
    """Download files from S3 to a local directory."""
    objects = s3.list_objects_v2(Bucket=BUCKET_NAME)

    print(objects)

    if 'Contents' not in objects:
        print("No files found in the specified bucket.")
        return

    for obj in objects['Contents']:
        filename = obj['Key']
        local_filename = os.path.join(LOCAL_DOWNLOAD_PATH, filename)
        local_folder_path = os.path.join(LOCAL_DOWNLOAD_PATH, os.path.dirname(filename))

        print(local_filename)
        os.makedirs(local_folder_path, exist_ok=True)
        s3.download_file(BUCKET_NAME, filename, local_filename)


def visualize_data(timestamps, temperatures, humidities, pressures):
    trace_temp = go.Scatter(x=timestamps, y=temperatures, mode='lines', name='Temperature')
    trace_hum = go.Scatter(x=timestamps, y=humidities, mode='lines', name='Humidity')
    trace_press = go.Scatter(x=timestamps, y=pressures, mode='lines', name='Pressure')

    return [trace_temp, trace_hum, trace_press]
    # layout = go.Layout(title='Visualization of Data')
    # return go.Figure(data=data, layout=layout)


# Callback to update the graph based on user input
@app.callback(
    Output('plot', 'figure'),
    [Input('dropdown', 'value')]
)
def update_graph(selected_option):
    # Create a Plotly figure based on the selected option

    fetch_files_from_s3()
    timestamps, temperatures, humidities, pressures = get_data_from_files(DATA_PATH)
    trace = visualize_data(timestamps, temperatures, humidities, pressures)

    layout = go.Layout(title='Graph Based on Dropdown Selection')
    figure = {'data': trace, 'layout': layout}

    return figure


# fetch_files_from_s3()
# timestamps, temperatures, humidities, pressures = get_data_from_files(LOCAL_DOWNLOAD_PATH + "/" + topic)
# trace = visualize_data(timestamps, temperatures, humidities, pressures)
# trace.show()

#
# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
