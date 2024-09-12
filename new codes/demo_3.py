import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from io import StringIO
import base64
import logging
import numpy as np
import plotly.graph_objs as go
from scipy.signal import find_peaks

from cards import UPDATE_card, PREVIEW_card, DETERMINISTIC_card, PROBABILISTIC_card

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Set up the layout with a 2x2 grid of cards
app.layout = html.Div(children=[
    html.H1(children='Analysis'),

    dbc.Row([
        dbc.Col(UPDATE_card(), width=6),
        dbc.Col(PREVIEW_card(), width=6),
    ]),
    
    dbc.Row([
        dbc.Col(DETERMINISTIC_card(), width=6),
        dbc.Col(PROBABILISTIC_card(), width=6),
    ]),
])

@app.callback(
    [Output('output-data-preview', 'children'),
     Output('x-variable', 'options'),
     Output('y-variable', 'options'),
     Output('cluster-graph', 'figure'),
     Output('inputqa', 'value')],
    [Input('upload-data', 'contents'),
     Input('x-variable', 'value'),
     Input('y-variable', 'value'),
     Input('graph-type', 'value')],
    [State('upload-data', 'filename')]
)
def update_output(contents, x_var, y_var, graph_type, filename):
    logging.debug("Callback triggered")
    if contents is not None:
        if not filename.endswith('.csv'):
            logging.error("Unsupported file type")
            return (html.Div(["Please upload a valid CSV file."]), [], [], {}, 10000)

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        try:
            df = pd.read_csv(StringIO(decoded.decode('utf-8')))
            logging.debug(f"DataFrame created with {len(df)} rows")
        except Exception as e:
            logging.error(f"Error parsing CSV: {e}")
            return (html.Div(["Error parsing CSV file. Please check the file format."]), [], [], {}, 10000)

        options = [{'label': col, 'value': col} for col in df.columns]

        figure = {}
        if x_var and y_var:
            figure = {
                'data': [
                    {'x': df[x_var], 'y': df[y], 'type': graph_type, 'name': y}
                    for y in y_var
                ],
                'layout': {
                    'title': 'Data Preview',
                    'xaxis': {'title': x_var},
                    'yaxis': {'title': ', '.join(y_var)}
                }
            }

            #find peak and clean input

        if 'Production' in df.columns and not df['Production'].empty:
            qa_value = df['Production'].iloc[0]
        else:
            qa_value = 10000

        return (html.Div([
                    html.H5(filename),
                    html.H6('Loaded successfully'),
                    html.P(f"Number of rows: {len(df)}")
                ]), 
                options, 
                options,
                figure,
                qa_value)

    return (html.Div(["Drag and drop or ", html.A("select a CSV file")]), [], [], {}, 10000)

@app.callback(
    Output('uncertainty-graph', 'figure'),
    [Input('prob-dist-button', 'value'),
     Input('Triangular-left', 'value'),
     Input('Triangular-right', 'value'),
     Input('Normal-std', 'value'),
     Input('inputqa', 'value')]
)
def update_probabilistic_graph(dist_type, tri_left, tri_right, normal_std, qa):
    figure = {
        'data': [],
        'layout': {
            'title': 'Uncertainty Analysis',
            'xaxis': {'title': 'Production Rate (qa)'},
            'yaxis': {'title': 'Probability Density'},
        }
    }

    x_values = np.linspace(0, 2 * qa, 500)

    if dist_type == "Triangular":
        mode = qa
        left = mode - mode * tri_left / 100
        right = mode + mode * tri_right / 100
        y_values = np.where((x_values >= left) & (x_values <= right),
                            (x_values - left) / (mode - left),
                            (right - x_values) / (right - mode))
        y_values = np.maximum(y_values, 0)
        figure['data'].append(go.Scatter(x=x_values, y=y_values, mode='lines', name='Triangular'))

    elif dist_type == "Normal":
        mean = qa
        std_dev = mean * normal_std / 100
        y_values = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_values - mean) / std_dev) ** 2)
        figure['data'].append(go.Scatter(x=x_values, y=y_values, mode='lines', name='Normal'))

    return figure

@app.callback(
    [Output('dca-graph', 'figure'),
     Output('selected-data-printout', 'children'),
     Output('DCA-parameters-printout', 'children')],
    [Input('ChecklistOptionsPeaks', 'value'),
     Input('ChecklistOptionsDeclineCurve', 'value'),
     Input('slider_numberofmonths', 'value')],
    [State('upload-data', 'contents'),
     State('x-variable', 'value'),
     State('upload-data', 'filename')]
)
def update_deterministic_analysis(peaks, decline_curves, num_months, contents, x_var, filename):
    figure = {
        'data': [],
        'layout': {
            'title': 'Deterministic Analysis',
            'xaxis': {'title': 'Time'},
            'yaxis': {'title': 'Value'}
        }
    }

    selected_data = "No data selected"
    parameters = "No parameters"

    if contents is not None:
        if not filename.endswith('.csv'):
            return figure, selected_data, parameters

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        try:
            df = pd.read_csv(StringIO(decoded.decode('utf-8')))
            logging.debug(f"DataFrame created with {len(df)} rows")
        except Exception as e:
            logging.error(f"Error parsing CSV: {e}")
            return figure, selected_data, parameters

        if 'Production' in df.columns:
            x_values = df[x_var] if x_var in df.columns else df.index
            y_values = df['Production']

            figure['data'].append(go.Scatter(x=x_values, y=y_values, mode='lines', name='Production'))

            if "showPeaks" in peaks:
                # Find peaks
                peaks_indices, _ = find_peaks(y_values)
                peak_x_values = x_values.iloc[peaks_indices]
                peak_y_values = y_values.iloc[peaks_indices]
                figure['data'].append(go.Scatter(x=peak_x_values, y=peak_y_values, mode='markers', name='Peaks', marker=dict(color='red', size=8)))

            if "showArpes" in decline_curves or "showDuong" in decline_curves:
                # Add logic for decline curves
                pass

            parameters = f"Number of months: {num_months}"

    return figure, selected_data, parameters

if __name__ == '__main__':
    app.run_server(debug=True)