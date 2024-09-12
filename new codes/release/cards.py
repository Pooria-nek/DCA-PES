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
        ],
        body=True,
        color="#F9F9F9",
    )

# Function to define PREVIEW_card
def PREVIEW_card(file_content_id='output-data-preview', x_var_id='x-variable', y_var_id='y-variable', graph_id='cluster-graph'):
    return dbc.Card(
        [
            html.H4("Preview data"),
            html.Div(id=file_content_id),
            dbc.Label("X variable"),
            dcc.Dropdown(
                id=x_var_id,
                options=[],
                multi=False
            ),
            dbc.Label("Y variable"),
            dcc.Dropdown(
                id=y_var_id,
                options=[],
                multi=True
            ),
            dbc.Row(dcc.Graph(id=graph_id)),  # Ensure this ID matches in the callback
        ],
        body=True,
        color="#F9F9F9",
    )

def DETERMINISTIC_card():
    return dbc.Card(
        [
            html.Div(id='output-data-upload22'),

            html.H2("Deterministic Analysis"),
            dcc.Checklist(
                id="ChecklistOptionsSum",
                options=[
                    {"label": "Show total", "value": "showTotal", "disabled": True},
                ],
                value=["showTotal"],
                labelStyle={"display": "inline-block"},
                inputStyle={"margin-left": "20px", "margin-right": "5px"}
            ),
            dcc.Checklist(
                id="ChecklistOptionsPeaks",
                options=[
                    {"label": "Show peaks", "value": "showPeaks"}
                ],
                value=[],
                labelStyle={"display": "inline-block"},
                inputStyle={"margin-left": "20px", "margin-right": "5px"}
            ),

            dcc.Checklist(
                id="ChecklistOptionsDeclineCurve",
                options=[
                    {"label": "Arpes decline curve", "value": "showArpes"},
                    {"label": "Duong decline curve", "value": "showDuong"}
                ],
                value=[],
                labelStyle={"display": "inline-block"},
                inputStyle={"margin-left": "20px", "margin-right": "5px"}
            ),

            html.Div(id='slider-output-container'),
            html.H5("Number of months to predict:"),
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
                dcc.Markdown("""
                    **Selection Data**

                    Choose the lasso or rectangle tool in the graph's menu
                    bar and then select points in the graph.

                    Note that if `layout.clickmode = 'event+select'`, selection data also
                    accumulates (or un-accumulates) selected data if you hold down the shift
                    button while clicking.
                """),
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
            html.H5("Economic limit production rate qa:"),
            dbc.Input(type="float", id='inputqa', value=10000),
            html.Div(id='textarea-Np-output', style={'whiteSpace': 'pre-line'}),
            dbc.Row([
                dbc.Col(dcc.Graph(id="uncertainty-graph"), md=6),
                dbc.Col([
                    dbc.Row([
                        dcc.RadioItems(
                            id='prob-dist-button',
                            options=[
                                {"label": "Triangular", "value": "Triangular"},
                                {"label": "Normal", "value": "Normal"},
                            ],
                            value="Triangular",
                            labelStyle={'display': 'block'}
                        )
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.InputGroupText("Triangular left:"),                        
                                dbc.Input(id="Triangular-left", placeholder="%", value=20, min=0, max=100)
                            ])
                        ]),
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.InputGroupText("Triangular right:"),                        
                                dbc.Input(id="Triangular-right", placeholder="%", value=20, min=0, max=100)
                            ])
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.InputGroupText("Normal STD %mean:"),                        
                                dbc.Input(id="Normal-std", placeholder="%", value=30, min=0, max=100)
                            ])
                        ])
                    ])
                ], md=6)
            ])
        ],
        body=True,
        color="#F9F9F9",
    )
