import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from io import StringIO
import base64
# from dash.dependencies import Input, Output, State
import logging

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
     Output('cluster-graph', 'figure')],
    [Input('upload-data', 'contents'),
     Input('x-variable', 'value'),
     Input('y-variable', 'value')],
    [State('upload-data', 'filename')]
)
def update_output(contents, x_var, y_var, filename):
    logging.debug("Callback triggered")
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        try:
            df = pd.read_csv(StringIO(decoded.decode('utf-8')))
            logging.debug(f"DataFrame created with {len(df)} rows")
        except Exception as e:
            logging.error(f"Error parsing CSV: {e}")
            return (html.Div(["Error parsing file"]), [], [], {})
        
        options = [{'label': col, 'value': col} for col in df.columns]
        
        # Create graph based on selected variables
        figure = {}
        if x_var and y_var:
            figure = {
                'data': [
                    {'x': df[x_var], 'y': df[y], 'type': 'line', 'name': y}
                    for y in y_var
                ],
                'layout': {
                    'title': 'Data Preview',
                    'xaxis': {'title': x_var},
                    'yaxis': {'title': ', '.join(y_var)}
                }
            }
        
        return (html.Div([
                    html.H5(filename),
                    html.H6('Loaded successfully'),
                    html.P(f"Number of rows: {len(df)}")
                ]), 
                options, 
                options,
                figure)
    
    return (html.Div(["Drag and drop or ", html.A("select files")]), [], [], {})

if __name__ == '__main__':
    app.run_server(debug=True)