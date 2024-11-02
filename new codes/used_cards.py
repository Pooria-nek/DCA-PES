import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd

# Function to define UPDATE_card
def UPDATE_card(upload_output_id='output-data-upload'):
    return dbc.Card(
        [
            html.H2("Data"),
            html.Hr(),
            dbc.Row([
                dbc.Col(children=[
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            "Drag and Drop or ", 
                            html.A("Select Files")]),
                        style={
                            "width": "100%",
                            "height": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderRadius": "5px",
                            "textAlign": "center",
                            "margin": "10px",
                        },
                        # Allow multiple files to be uploaded
                        multiple=False,
                    ),
                ]),
            ], style={'width': '100%', 'padding': '5px 5px', 'display': 'inline-block'}),
            
            # Checklist
            dbc.Row(children=[
                dbc.Row(children=[
                    html.H4("Select data columns", style={"margin-left": "25px","margin-right": "5px"})],
                    ),
        
                dbc.Row(children=[
                    dcc.Checklist(
                        id="checklistfiles",
                        labelStyle={'display': 'block'},
                        inputStyle={"margin-left": "20px","margin-right": "5px"}
                    )
                ])],

                style={'width': '100%', 'padding': '5px 5px', 'display': 'inline-block'},
            ),
        ],
        body=True,
        color="#F9F9F9",
    )

# Function to define PREVIEW_card
def PREVIEW_card(file_content_id='output-data-preview', x_var_id='x-variable', y_var_id='y-variable', graph_id='cluster-graph', graph_type_id='graph-type'):
    return dbc.Card(
        [
            html.H4("Preview data"),
            html.Div(id=file_content_id),  # Displays file details (filename, number of rows, etc.)
            
            dbc.Label("X variable"),
            dcc.Dropdown(
                id=x_var_id,
                options=[{"label": col, "value": col} for col in pd.DataFrame()],
                multi=False  # Single-select for X variable
            ),
            
            dbc.Label("Y variable"),
            dcc.Dropdown(
                id=y_var_id,
                options=[{"label": col, "value": col} for col in pd.DataFrame()],
                multi=True  # Multi-select for Y variables
            ),

            dbc.Label("select Slice"),
            dcc.Dropdown(
                id='slice_variable',
                options=[{"label": col, "value": col} for col in pd.DataFrame()],
                multi=True  # Multi-select for Y variables
            ),
            
            # Graph type selection dropdown
            html.Div([
                html.Label('Select Graph Type'),
                dcc.Dropdown(
                    id=graph_type_id,  # This ID will be used in the callback
                    options=[
                        {'label': 'Line', 'value': 'line'},
                        # {'label': 'Scatter', 'value': 'scatter'},
                        {'label': 'Bar', 'value': 'bar'}
                    ],
                    value='line'  # Default graph type
                )
            ]),

            # Graph to display the data
            dbc.Row(dcc.Graph(id=graph_id)),  # Render graph here
        ],
        body=True,
        color="#F9F9F9",
    )