import dash
import dash_core_components as dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import base64
import numpy as np
from scipy.signal import find_peaks
import io
from DCA04 import *
from used_cards import UPDATE_card, PREVIEW_card

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='Analysis => demo_5'),
    dcc.Store(id='dataframevalue'),
    dbc.Row([
        dbc.Col(UPDATE_card(), width=6),
        dbc.Col(PREVIEW_card(), width=6),
    ]),
])

@app.callback(
    [
        Output('checklistfiles', 'options'),
        Output('dataframevalue', 'data'),
        Output('x-variable', 'options'),
        Output('y-variable', 'options'),
        Output('slice_variable', 'options'),
        Output('cluster-graph', 'figure')
    ],
    [
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        Input('x-variable', 'value'),
        Input('y-variable', 'value'),
        Input('slice_variable', 'value'),
        Input('graph-type', 'value')
    ],
    prevent_initial_call=True
)
def update_output(icontents, ifilename, x_var, y_var, s_var, graph_type):
    if icontents is None:
        raise dash.exceptions.PreventUpdate  # Prevent the callback from updating if no file is uploaded

    try:
        # Parse the uploaded data
        dff, dffPeaks, dateCol, non_nan_indices = parse_data(icontents, ifilename, [''])

        # Checklist options for data columns
        checklist_options = [{"label": col, "value": col} for col in dff.columns]
        
        # Options for dropdowns
        dropdown_options = [{'label': col, 'value': col} for col in dff.columns]
        
        # Slice selector based on detected peaks
        slice_selector = [{'label': f'Slice {i}', 'value': i} for i in range(len(dffPeaks))]

        # Select the slice of data if s_var is provided
        sdf = dff.iloc[s_var] if s_var else dff

        print(sdf)
        
        # Sort the sliced data
        sdf = sdf.sort_index()

        # Default figure structure if no variables are selected
        figure = {'data': [], 'layout': {'title': 'Data Preview'}}

        # Generate figure if X and Y variables are selected
        if x_var and y_var:
            figure = {
                'data': [
                    {'x': sdf[x_var], 'y': sdf[y], 'type': graph_type, 'name': y} for y in y_var
                ],
                'layout': {
                    'title': 'Data Preview',
                    'xaxis': {'title': x_var},
                    'yaxis': {'title': ', '.join(y_var)}
                }
            }
        
        # Return all the options and the figure
        return checklist_options, dff.to_json(date_format='iso', orient='split'), dropdown_options, dropdown_options, slice_selector, figure

    except Exception as e:
        print("Error processing file:", e)
        return [{}], None, [], [], [], {
            'data': [],
            'layout': {'title': 'Error: Could not process file', 'xaxis': {}, 'yaxis': {}}
        }

def parse_data(contents, filename, date_columns=[]):
    """
    Parses CSV data from uploaded contents and detects peaks.
    
    Parameters:
        contents (str): Base64 encoded contents of the uploaded file.
        filename (str): Name of the uploaded file to check file type.
        date_columns (list): List of potential date columns to parse if any.
        
    Returns:
        dff (pd.DataFrame): Parsed DataFrame from the file.
        dffPeaks (pd.Series): Indices of rows with detected peaks in data.
        dateCol (str or None): Name of the detected date column, if any.
        non_nan_indices (list): List of indices with non-NaN data points.
    """
    # Decode and read the uploaded file contents
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    dff = pd.DataFrame()
    dateCol = None

    try:
        # Check if file is CSV, then load it
        if filename.endswith('.csv'):
            dff = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        else:
            raise ValueError("Unsupported file type. Please upload a CSV file.")
        
        # Parse date columns if specified
        for col in date_columns:
            if col in dff.columns:
                dff[col] = pd.to_datetime(dff[col], errors='coerce')
                dateCol = col  # Set the first detected date column as the primary date column
        
        # Drop rows with NaN values
        dff.dropna(inplace=True)
        
        # Detect peaks on the first numeric column for simplicity (you may adjust for specific column)
        numeric_cols = dff.select_dtypes(include='number').columns
        if numeric_cols.any():
            primary_col = numeric_cols[0]  # Assume the first numeric column for peak detection
            peaks, _ = find_peaks(dff[primary_col])
            dffPeaks = dff.iloc[peaks]
        else:
            dffPeaks = pd.DataFrame()  # Empty DataFrame if no numeric columns are found
        
        # Get indices of non-NaN rows (for reference in analysis)
        non_nan_indices = dff.index.tolist()

    except Exception as e:
        print("Error parsing data:", e)
        return pd.DataFrame(), pd.DataFrame(), None, []

    return dff, dffPeaks, dateCol, non_nan_indices

if __name__ == '__main__':
    app.run_server(debug=True)