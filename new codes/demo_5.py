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
from used_cards import UPDATE_card, PREVIEW_card, DETERMINISTIC_card, PROBABILISTIC_card
from scipy.optimize import curve_fit

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
    dbc.Row([
        dbc.Col(DETERMINISTIC_card(), width=6),
        dbc.Col(PROBABILISTIC_card(), width=6),
    ]),
    dbc.Spinner(html.Div(id="loading-output")),
    html.Div(id='error-message', style={'color': 'red'}),
    html.Button("Download Data", id="btn-download"),
    dcc.Download(id="download-dataframe-csv")
])

@app.callback(
    [
        Output('checklistfiles', 'options'),
        Output('dataframevalue', 'data'),
        Output('x-variable', 'options'),
        Output('y-variable', 'options'),
        Output('slice_variable', 'options'),
        Output('cluster-graph', 'figure'),
        Output('error-message', 'children')
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
        # print("dff")
        # print(dff)

        # Checklist options for data columns
        checklist_options = [{"label": col, "value": col} for col in dff.columns]
        
        # Options for dropdowns
        dropdown_options = [{'label': col, 'value': col} for col in dff.columns]

        # print("dffPeaks")
        # print(dffPeaks)
        
        # Slice selector based on detected peaks, starting with a 0 value
        slice_selector = [{'label': 'Slice 0', 'value': 0}] + [{'label': f'Slice {i+1}', 'value': dffPeaks.index[i]} for i in range(len(dffPeaks))]

        # print("slice_selector")
        # print(slice_selector)

        # print("s_var")
        # print(s_var)

        # If more than 2 values in s_var, print dff value from first to second s_var value
        if s_var and len(s_var) > 1:
            print(dff.iloc[s_var[0]:s_var[1]])
            sdf = dff.iloc[s_var[0]:s_var[1]]
        else:
            sdf = dff
            
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

            # Add a new trace for the points you want to show differently
            if not dffPeaks.empty:
                figure['data'].append({
                    'x': dffPeaks[x_var],
                    'y': dffPeaks[y_var[0]],  # Assuming you want to highlight the first y variable
                    'mode': 'markers',
                    'marker': {'color': 'red', 'size': 5},
                    'name': 'Peaks'
                })
        
        # Return all the options and the figure
        return checklist_options, dff.to_json(date_format='iso', orient='split'), dropdown_options, dropdown_options, slice_selector, figure, ""

    except Exception as e:
        print("Error processing file:", e)
        return [{}], None, [], [], [], {
            'data': [],
            'layout': {'title': 'Error: Could not process file', 'xaxis': {}, 'yaxis': {}}
        }, f"Error processing file: {e}"

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-download", "n_clicks"),
    State('dataframevalue', 'data'),
    prevent_initial_call=True
)
def download_data(n_clicks, data):
    if data is None:
        raise dash.exceptions.PreventUpdate
    dff = pd.read_json(data, orient='split')
    return dcc.send_data_frame(dff.to_csv, "processed_data.csv")

# @app.callback(
#     Output('dca-graph', 'figure'),
#     [
#         Input('ChecklistOptionsSum', 'value'),
#         Input('ChecklistOptionsPeaks', 'value'),
#         Input('ChecklistOptionsDeclineCurve', 'value'),
#         Input('slider_numberofmonths', 'value'),
#         State('dataframevalue', 'data')
#     ]
# )
# def update_deterministic_graph(show_total, show_peaks, decline_curve, num_months, data):
#     # if data is None:
#     #     raise dash.exceptions.PreventUpdate

#     dff = pd.read_json(data, orient='split')
#     print("Data for deterministic graph:")
#     print(dff)
#     figure = {'data': [], 'layout': {'title': 'Deterministic Analysis'}}

#     # Add traces based on the checklist options
#     if 'showTotal' in show_total:
#         numeric_dff = dff.select_dtypes(include=[np.number])  # Select only numeric columns
#         figure['data'].append({
#             'x': numeric_dff.index,
#             'y': numeric_dff.sum(axis=1),
#             'type': 'line',
#             'name': 'Total'
#         })

#     if 'showPeaks' in show_peaks:
#         peaks, _ = find_peaks(dff.iloc[:, 0])  # Assuming the first column for simplicity
#         figure['data'].append({
#             'x': dff.index[peaks],
#             'y': dff.iloc[peaks, 0],
#             'mode': 'markers',
#             'marker': {'color': 'red', 'size': 5},
#             'name': 'Peaks'
#         })

#     # Add decline curve traces
#     if 'showArps' in decline_curve:
#         # Example Arps decline curve logic
#         # Assuming 'time' is the index and 'production' is the column to fit the curve

#         def arps_decline(t, qi, di, b):
#             return qi / ((1 + b * di * t) ** (1 / b))

#         time = np.arange(len(dff))
#         production = dff.iloc[:, 0]  # Assuming the first column for simplicity

#         # Fit the Arps decline curve
#         try:
#             popt, _ = curve_fit(arps_decline, time, production, maxfev=10000)
#             qi, di, b = popt

#             # Generate fitted values
#             fitted_values = arps_decline(time, qi, di, b)

#             # Add the fitted curve to the figure
#             figure['data'].append({
#                 'x': dff.index,
#                 'y': fitted_values,
#                 'type': 'line',
#                 'name': 'Arps Decline Curve',
#                 'line': {'dash': 'dash'}
#             })
#         except Exception as e:
#             print("Error fitting Arps decline curve:", e)

#     if 'showDuong' in decline_curve:
#         # Add Duong decline curve logic here
#         pass

#     print("Figure data:")
#     print(figure['data'])
#     return figure

# @app.callback(
#     Output('uncertainty-graph', 'figure'),
#     [
#         Input('inputqa', 'value'),
#         Input('prob-dist-button', 'value'),
#         Input('Triangular-left', 'value'),
#         Input('Triangular-right', 'value'),
#         Input('Normal-std', 'value'),
#         State('dataframevalue', 'data')
#     ]
# )
# def update_probabilistic_graph(qa, dist_type, tri_left, tri_right, norm_std, data):
#     if data is None:
#         raise dash.exceptions.PreventUpdate

#     dff = pd.read_json(data, orient='split')
#     figure = {'data': [], 'layout': {'title': 'Probabilistic Analysis'}}

#     # Add probabilistic analysis logic here based on the selected distribution type
#     if dist_type == 'Triangular':
#         # Add Triangular distribution logic here
#         pass
#     elif dist_type == 'Normal':
#         # Add Normal distribution logic here
#         pass

#     return figure

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