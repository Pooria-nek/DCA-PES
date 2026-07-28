import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd

# Function to define UPDATE_card
def UPDATE_card(upload_output_id='output-data-upload'):
    return dbc.Card(
        [
            html.H2("Data Upload"),
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
                    html.H4("Select Data Columns", style={"margin-left": "25px","margin-right": "5px"})],
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
            html.H4("Data Preview"),
            html.Div(id=file_content_id),  # Displays file details (filename, number of rows, etc.)
            
            dbc.Label("X Variable"),
            dcc.Dropdown(
                id=x_var_id,
                options=[{"label": col, "value": col} for col in pd.DataFrame()],
                multi=False  # Single-select for X variable
            ),
            
            dbc.Label("Y Variable"),
            dcc.Dropdown(
                id=y_var_id,
                options=[{"label": col, "value": col} for col in pd.DataFrame()],
                multi=True  # Multi-select for Y variables
            ),

            dbc.Label("Select Slice"),
            dcc.Dropdown(
                id='slice_variable',
                options=[{"label": col, "value": col} for col in pd.DataFrame()],
                multi=True  # Multi-select for slices
            ),
            
            # Graph type selection dropdown
            html.Div([
                html.Label('Select Graph Type'),
                dcc.Dropdown(
                    id=graph_type_id,  # This ID will be used in the callback
                    options=[
                        {'label': 'Line', 'value': 'line'},
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


def DETERMINISTIC_card():
    return dbc.Card(
        [
            html.H2("Deterministic Analysis"),
            dcc.Checklist(
                id="ChecklistOptionsSum",
                options=[
                    {"label": "Show Total", "value": "showTotal"},
                ],
                value=["showTotal"],
                labelStyle={"display": "inline-block"},
                inputStyle={"margin-left": "20px", "margin-right": "5px"}
            ),
            dcc.Checklist(
                id="ChecklistOptionsPeaks",
                options=[
                    {"label": "Show Peaks", "value": "showPeaks"}
                ],
                value=[],
                labelStyle={"display": "inline-block"},
                inputStyle={"margin-left": "20px", "margin-right": "5px"}
            ),

            dcc.Checklist(
                id="ChecklistOptionsDeclineCurve",
                options=[
                    {"label": "Arps Decline Curve", "value": "showArps"},
                    {"label": "Duong Decline Curve", "value": "showDuong"}
                ],
                value=[],
                labelStyle={"display": "inline-block"},
                inputStyle={"margin-left": "20px", "margin-right": "5px"}
            ),

            html.Div(id='slider-output-container'),
            html.H5("Number of Months to Predict:"),
            dcc.Slider(
                id="slider_numberofmonths",
                min=1,
                max=100,
                marks={
                    1: '1',
                    20: '20',
                    40: '40',
                    60: '60',
                    80: '80',
                    100: '100'
                },
                tooltip={"placement": "bottom", "always_visible": True},
                step=1,
                value=20),
            html.Div([
                dbc.Row(dcc.Graph(id="dca-graph")),
            ], style={"height": "200", "width": "80vh"}),
            html.Div([
                dbc.Row([
                    dbc.Col(
                        html.Pre(id='selected-data-printout', style={'whiteSpace': 'pre-line'}), md=2),
                    dbc.Col(
                        html.Pre(id='DCA-parameters-printout', style={'whiteSpace': 'pre-line'}), md=2),
                ])
            ], className='three columns'),
        ],
        body=True,
        color="#F9F9F9",
    )

def PROBABILISTIC_card():
    return dbc.Card(
        [
            html.H2("Probabilistic Analysis"),
            
            # Economic limit production rate input
            html.H5("Economic Limit Production Rate (qa):"),
            dbc.Input(type="number", id='inputqa', value=10000),
            
            # Output display for text (Np output)
            html.Div(id='textarea-Np-output', style={'whiteSpace': 'pre-line'}),
            
            dbc.Row([
                # Graph for uncertainty analysis
                dbc.Col(dcc.Graph(id="uncertainty-graph"), md=6),
                
                dbc.Col([
                    # Radio buttons for selecting probability distribution
                    dbc.Row([
                        dcc.RadioItems(
                            id='prob-dist-button',
                            options=[
                                {"label": "Triangular", "value": "Triangular"},
                                {"label": "Normal", "value": "Normal"},
                            ],
                            value="Triangular",  # Default to Triangular
                            labelStyle={'display': 'block'}
                        )
                    ]),
                    
                    # Inputs for Triangular distribution
                    dbc.Row([
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.InputGroupText("Triangular Left:"),                        
                                dbc.Input(id="Triangular-left", type="number", placeholder="%", value=20, min=0, max=100)
                            ])
                        ]),
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.InputGroupText("Triangular Right:"),                        
                                dbc.Input(id="Triangular-right", type="number", placeholder="%", value=20, min=0, max=100)
                            ])
                        ])
                    ]),
                    
                    # Input for Normal distribution
                    dbc.Row([
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.InputGroupText("Normal STD % Mean:"),                        
                                dbc.Input(id="Normal-std", type="number", placeholder="%", value=30, min=0, max=100)
                            ])
                        ])
                    ])
                ], md=6)
            ])
        ],
        body=True,
        color="#F9F9F9",
    )