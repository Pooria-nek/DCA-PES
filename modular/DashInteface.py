import base64
import io
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash import dash_table
import numpy as np
import pickle
import json

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modular.DCA04 import *


external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
]
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
app = dash.Dash(external_stylesheets=external_stylesheets)


uploadSection = dbc.Card(
    [
        html.H2([
            html.I(className="bi bi-upload me-2"),
            "Data"
        ]),
        html.Hr(),

        # File Upload Section
        dbc.Row([
            dbc.Col([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "marginBottom": "5px",
                    },
                    multiple=True,
                ),
                html.Small("Upload CSV files with production data", className="text-muted", style={"marginLeft": "10px"}),
            ]),
        ]),

        html.Br(),

        # Checklist Section (dynamic options from callback)
        dbc.Card(
            dbc.CardBody([
                html.H5("Select data columns", className="mb-2"),
                dcc.Checklist(
                    id="checklistfiles",
                    options=[],  # دینامیک از طریق callback تنظیم می‌شه
                    value=[],
                    labelStyle={'display': 'block', 'marginBottom': '4px'},
                    inputStyle={"marginLeft": "10px", "marginRight": "5px"}
                )
            ]),
            className="border border-secondary-subtle",
            style={"backgroundColor": "#ffffff", "padding": "10px", "borderRadius": "6px"}
        ),
        
        # Graph section
        dbc.Card(
            dcc.Graph(id="data-preview-graph"),
            body=True,
            className="mt-2",
            style={
                "height": "500px",
                "backgroundColor": "#ffffff",
                "border": "1px solid #dee2e6",
                "borderRadius": "6px",
                "padding": "10px"
            }
        ),
    ],
    body=True,
    color="#F9F9F9",
    className="shadow-sm"
)

#-----------------------------------------------------------------------------
cleaningSection = dbc.Card(
    [
        html.H4([
            html.I(className="bi bi-graph-up-arrow me-2"),
            "Preview Data"
        ]),
        html.Div(id='output-data-upload21'),
        html.Br(),

        dbc.Label("X variable", className="fw-bold"),
        dcc.Dropdown(
            id="x-variable",
            options=[  # Placeholder options; dynamically filled later
                {"label": col, "value": col} for col in pd.DataFrame()
            ],
            multi=False,
            placeholder="Select X variable"
        ),
        html.Br(),

        dbc.Label("Y variable", className="fw-bold"),
        dcc.Dropdown(
            id="y-variable",
            options=[  # Placeholder options; dynamically filled later
                {"label": col, "value": col} for col in pd.DataFrame()
            ],
            multi=True,
            placeholder="Select one or more Y variables"
        ),
        html.Br(),

        # Monthly and Y2 options
        dbc.Row([
            dbc.Col(
                dcc.Checklist(
                    id="ChecklistOptionsMonth",
                    options=[{"label": "Monthly data", "value": "Month"}],
                    value=["Month"],
                    labelStyle={"display": "inline-block"},
                    inputStyle={"marginLeft": "10px", "marginRight": "5px"},
                    style={"marginBottom": "10px"}
                ),
                width="auto"
            ),
            dbc.Col(
                dcc.Checklist(
                    id="ChecklistOptionsY2",
                    options=[{"label": "Double Y-Axis", "value": "y2"}],
                    value=[],
                    labelStyle={"display": "inline-block"},
                    inputStyle={"marginLeft": "10px", "marginRight": "5px"},
                ),
                width="auto"
            )
        ], justify="start"),
        html.Br(),

        # Graph section
        dbc.Card(
            dcc.Graph(id="cluster-graph"),
            body=True,
            className="mt-2",
            style={
                "height": "500px",
                "backgroundColor": "#ffffff",
                "border": "1px solid #dee2e6",
                "borderRadius": "6px",
                "padding": "10px"
            }
        ),
    ],
    body=True,
    color="#F9F9F9",
    className="shadow-sm"
)



controls22 = dbc.Card(
    [
        html.H4([
            html.I(className="bi bi-bar-chart-line-fill me-2"),
            "Deterministic Analysis"
        ]),
        html.Div(id='output-data-upload22'),
        html.Br(),

        dbc.Checklist(
            id="ChecklistOptionsSum",
            options=[
                {"label": "Show total", "value": "showTotal", "disabled": True}
            ],
            value=["showTotal"],
            inline=True,
            inputStyle={"marginLeft": "10px", "marginRight": "5px"},
            style={"marginBottom": "10px"}
        ),

        dbc.Checklist(
            id="ChecklistOptionsPeaks",
            options=[
                {"label": "Show peaks", "value": "showPeaks"}
            ],
            value=[],
            inline=True,
            inputStyle={"marginLeft": "10px", "marginRight": "5px"},
            style={"marginBottom": "10px"}
        ),

        dbc.Checklist(
            id="ChecklistOptionsDeclineCurve",
            options=[
                {"label": "Arps decline curve", "value": "showArpes"},
                {"label": "Duong decline curve", "value": "showDuong"}
            ],
            value=[],
            inline=False,
            inputStyle={"marginLeft": "10px", "marginRight": "5px"},
            style={"marginBottom": "15px"}
        ),

        html.H6("Number of months to predict:", className="fw-bold"),
        dcc.Slider(
            id="slider_numberofmonths",
            min=1,
            max=100,
            step=1,
            value=20,
            marks={i: str(i) for i in [1, 20, 40, 60, 80, 100]},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
        html.Br(),

        dbc.Card(
            dcc.Graph(id="dca-graph"),
            body=True,
            className="mt-2",
            style={
                "height": "400px",
                "backgroundColor": "#ffffff",
                "border": "1px solid #dee2e6",
                "borderRadius": "6px",
                "padding": "10px"
            }
        ),

        html.Br(),

        dbc.Row([
            dbc.Col([
                html.H6("Selected Data"),
                html.Pre(id='selected-data-printout', style=styles['pre']),
            ], md=6),

            dbc.Col([
                html.H6("DCA Parameters"),
                html.Pre(id='DCA-parameters-printout', style=styles['pre']),
            ], md=6),
        ]),

        html.Div([
            dcc.Markdown("""
                **Tip**: Use the lasso or rectangle tool in the graph menu bar to select points.
                If `layout.clickmode = 'event+select'`, holding `Shift` allows multi-selection.
            """, className="text-muted")
        ], className="mt-3")
    ],
    body=True,
    color="#F9F9F9",
    className="shadow-sm"
)



controls3 = dbc.Card(
    [
        html.H4([
            html.I(className="bi bi-graph-up-arrow me-2"),
            "Probabilistic Analysis"
        ]),
        html.H6("Economic limit production rate (qa):", className="fw-bold"),
        dbc.Input(
            type="number", id='inputqa', value=10000,
            placeholder="Enter economic limit (qa)",
            style={"marginBottom": "10px"}
        ),

        html.Div(id='textarea-Np-output', style={'whiteSpace': 'pre-line'}),

        dbc.Row([
            # Graph
            dbc.Col(dcc.Graph(id="uncertainty-graph"), md=7),

            # Distribution Inputs
            dbc.Col([
                html.H6("Probability Distribution", className="fw-bold"),
                dcc.RadioItems(
                    id='prob-dist-button',
                    options=[
                        {"label": "Triangular", "value": "Triangular"},
                        {"label": "Normal", "value": "Normal"},
                    ],
                    value='Triangular',
                    labelStyle={"display": "block", "marginBottom": "5px"},
                    style={"marginBottom": "15px"}
                ),

                html.Div([
                    html.H6("Triangular Parameters", className="fw-bold"),
                    dbc.InputGroup([
                        dbc.InputGroupText("Left %"),
                        dbc.Input(
                            id="Trinangular-left",
                            placeholder="e.g. 20", value=20,
                            min=0, max=100, type="number"
                        )
                    ], className="mb-2"),

                    dbc.InputGroup([
                        dbc.InputGroupText("Right %"),
                        dbc.Input(
                            id="Trinangular-right",
                            placeholder="e.g. 20", value=20,
                            min=0, max=100, type="number"
                        )
                    ], className="mb-3"),
                ]),

                html.Div([
                    html.H6("Normal Parameters", className="fw-bold"),
                    dbc.InputGroup([
                        dbc.InputGroupText("STD % of mean"),
                        dbc.Input(
                            id="Normal-std",
                            placeholder="e.g. 30", value=30,
                            min=0, max=100, type="number"
                        )
                    ])
                ])
            ], md=5)
        ])
    ],
    body=True,
    color="#F9F9F9",
    className="shadow-sm"
)



#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#---------------------LAYOUT---------------------------------------------------
#------------------------------------------------------------------------------
app.layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Card(
                    [
                        dbc.CardHeader(html.H1("PES Tool for Decline Curve Analysis", className="text-center mb-0")),
                        dbc.CardBody(
                            [
                                html.Hr(),
                                dcc.Store(id='dataframevalue'),
                                dcc.Store(id='dataframepeaksvalue'),
                                dcc.Store(id='dataframepeaksvalueUseForDCA'),

                                dbc.Row(
                                    [
                                        dbc.Col(uploadSection, md=12),
                                    ],
                                    className="mb-4"
                                ),

                                html.Div(id='div1', className="mb-4"),

                                dbc.Row(
                                    [
                                        dbc.Col(cleaningSection, md=12),
                                    ],
                                    className="mb-4"
                                ),

                                html.Div(id='div1', className="mb-4"),

                                dbc.Card(
                                    [
                                        dbc.CardHeader("Peak Detection & Forecasting"),
                                        dbc.CardBody(
                                            dbc.Row(
                                                [
                                                    dbc.Col(controls22, md=6),
                                                    dbc.Col(controls3, md=6),
                                                ]
                                            )
                                        ),
                                    ],
                                    className="mb-4"
                                ),

                                html.Div(id='div2', className="mb-4"),

                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dash_table.DataTable(
                                                id='DataTable',
                                                export_format="csv",
                                                style_data={'border': '1px solid #dee2e6', 'padding': '8px'},
                                                style_header={
                                                    'backgroundColor': '#f8f9fa',
                                                    'fontWeight': 'bold',
                                                    'border': '1px solid #dee2e6',
                                                    'whiteSpace': 'normal'
                                                },
                                                style_cell={
                                                    'fontSize': 16,
                                                    'font-family': 'sans-serif',
                                                    'textAlign': 'center'
                                                },
                                                style_table={
                                                    'overflowX': 'auto',
                                                    'border': '1px solid #dee2e6',
                                                    'marginTop': '10px'
                                                }
                                            ),
                                            width=12
                                        )
                                    ]
                                ),
                            ]
                        ),
                    ],
                    className="shadow-sm mb-4",
                    style={"backgroundColor": "white", "borderRadius": "0.75rem"}
                )
            ],
            fluid=True,
            style={"padding": "2rem", "backgroundColor": "#f4f6f9"}
        )
    ],
    id="mainContainer",
    style={"display": "flex", "flexDirection": "column", "minHeight": "100vh"}
)



@app.callback(
    Output("DataTable", "css"), Input("DataTable", "derived_virtual_data"),
)
def style_export_button(data):
    if data == []:
        return [{"selector": ".export", "rule": "display:none"}]
    else:
        return [{"selector": ".export", "rule": "display:block"}]

#------------------------------------------------------------------------------
# Updating columns check list
@app.callback([
    Output(component_id='checklistfiles', component_property='options'),
               Output('dataframevalue', 'data'),
               Output('dataframepeaksvalue', 'data'),
                ],
              [Input(component_id='upload-data', component_property='contents'),
               State(component_id='upload-data', component_property='filename'),
               State(component_id='upload-data', component_property='last_modified')],
              prevent_initial_call=True)
def update_output(icontents, ifilename, date):
    dff = pd.DataFrame(columns=["Date"])
    dffPeaks = pd.DataFrame(columns=["Date"])
    dff = dff.set_index("Date")
    dffPeaks = dffPeaks.set_index("Date")   
    if icontents:
        for i,contents in enumerate(icontents):
            contents = icontents[i]
            filename = ifilename[i]

            df1,dfPeaks1,dateCol = parse_data(contents, filename,[''])
            df1 = df1.set_index(dateCol)
            dfPeaks1 = dfPeaks1.set_index(dateCol)
    
            dff = pd.concat([dff, df1], axis=1)
            dffPeaks = pd.concat([dffPeaks, dfPeaks1], axis=1)
        
        dffPeaks['ShowOnGraph'] = False    

        if "index" in dff.columns:
            dff.drop("index", axis=1, inplace=True)
        if "index" in dffPeaks.columns:
            dffPeaks.drop("index", axis=1, inplace=True) 

        dff=dff.reset_index()
        dffPeaks=dffPeaks.reset_index()
        dffPeaksUseForDCA=pd.concat([dffPeaks[dateCol], dffPeaks['ShowOnGraph']], axis=1)

    checklist_options = [{"label": f"{col}", "value": col} for col in dff.columns.to_list()]
    # checklist_options = [{"label": f"{filename} : {col}", "value": col} for col in df1.columns.to_list()]

    return [checklist_options,
            dff.to_json(date_format='iso', orient='split'),
            dffPeaks.to_json(date_format='iso', orient='split')]

@app.callback(
    Output("data-preview-graph", "figure"),
    Input("checklistfiles", "value"),
    State("dataframevalue", "data"),
)
def update_graph(selected_columns, jsonified_df):
    if not selected_columns or not jsonified_df:
        return go.Figure()

    df = pd.read_json(jsonified_df, orient='split')

    fig = go.Figure()

    for col in selected_columns:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df["Date"], y=df[col], mode='lines+markers', name=col))

    fig.update_layout(
        title="Selected Data Columns",
        xaxis_title="Date",
        yaxis_title="Values",
        template="plotly_white"
    )

    return fig
#------------------------------------------------------------------------------

# updating the dropdown of x and y for graph by browsed files
@app.callback(
    [
          Output('x-variable', 'options'),
          Output('y-variable', 'options'),
          Output('x-variable', 'value'),
          Output('y-variable', 'value'),
    ],
    [
        Input('upload-data', 'contents'),
        Input('upload-data', 'filename'),
        Input('dataframevalue', 'data'),
        Input('dataframepeaksvalue', 'data'),
        # Input("ChecklistOptionsMonth", "value"),        
    ],
)

def update_date_dropdown(icontents, ifilename,dfvalue,dfPeaksvalue):
    
    xlabel=""
    ylabel=""
    dff = pd.DataFrame(columns=["Date"])
    dffPeaks = pd.DataFrame(columns=["Date"])
    dff = dff.set_index("Date")
    dffPeaks = dffPeaks.set_index("Date")
    
    if icontents:
    #     for i,contents in enumerate(icontents):
    #         contents = icontents[i]
    #         filename = ifilename[i]
    #         df1,dfPeaks1,dateCol = parse_data(contents, filename,[''])
    #         df1 = df1.set_index(dateCol)
    #         dfPeaks1 = dfPeaks1.set_index(dateCol)
    
    #         dff = pd.concat([dff, df1], axis=1)
    #         dffPeaks = pd.concat([dffPeaks, dfPeaks1], axis=1)
        
    #     dff.drop("index", axis=1, inplace=True)
    #     dffPeaks.drop("index", axis=1, inplace=True)   
    #     dff=dff.reset_index()
    #     dffPeaks=dffPeaks.reset_index()


        dff=pd.read_json(dfvalue, orient='split')
        dffPeaks=pd.read_json(dfPeaksvalue, orient='split')
        xlabel=dff.columns[0]
        ylabel=dff.columns[1]

        
        return [{'label': col, 'value': col} for col in dff.columns],[{'label': col, 'value': col} for col in dff.columns],str(xlabel),str(ylabel)
    else:
        raise dash.exceptions.PreventUpdate
#------------------------------------------------------------------------------
@app.callback([
     Output('selected-data-printout', 'children'),
     Output('dataframepeaksvalueUseForDCA', 'data'),
    ],     
    [Input('dca-graph', 'selectedData')],
    [State('dataframepeaksvalue', 'data')]
    )
def display_selected_data(selectedDatas,dfPeaks):
    # #mj=selectedDatas
    # sample_list = [selectedDatas,dfPeaksvalue]
    # file_name = "GraphSelectedData.pkl"
    # open_file = open(file_name, "wb")
    # pickle.dump(sample_list, open_file)
    # open_file.close()
    dfPeaksvalue=pd.read_json(dfPeaks, orient='split')
    dfPeaksvalue['ShowOnGraph']=False
    for ii in  range(len(selectedDatas['points'])):
          # 
          mjddf=dfPeaksvalue.loc[dfPeaksvalue['Date'] == selectedDatas['points'][ii]['x']]
          mjddf=mjddf.reset_index()
          dfPeaksvalue['ShowOnGraph'].loc[mjddf.iloc[0,0]] = True

    return json.dumps(selectedDatas, indent=2), dfPeaksvalue.to_json(date_format='iso', orient='split')

#------------------------------------------------------------------------------
@app.callback(
   Output(component_id='Trinangular-right', component_property='style'),
   [Input(component_id='prob-dist-button', component_property='value')])

def show_hide_element(DistRadioButton):
    if DistRadioButton == 'Normal':
        return {'display': 'none'}
    if DistRadioButton == 'Triangular':
        return {'display': 'block'}
   
#------------------------------------------------------------------------------
@app.callback(
   Output(component_id='Trinangular-left', component_property='style'),
   [Input(component_id='prob-dist-button', component_property='value')])

def show_hide_element(DistRadioButton):
    if DistRadioButton == 'Normal':
        return {'display': 'none'}
    if DistRadioButton == 'Triangular':
        return {'display': 'block'}
   
#------------------------------------------------------------------------------
@app.callback(
   Output(component_id='Normal-std', component_property='style'),
   [Input(component_id='prob-dist-button', component_property='value')])

def show_hide_element(DistRadioButton):
    if DistRadioButton == 'Normal':
        return {'display': 'block'}
    if DistRadioButton == 'Triangular':
        return {'display': 'none'}
   
#------------------------------------------------------------------------------
@app.callback([
    Output('DCA-parameters-printout', 'children'),
    Output("textarea-Np-output", "children"),
    Output("cluster-graph", "figure"),
    Output("dca-graph", "figure"),
    Output("uncertainty-graph", "figure"),
    Output('DataTable', 'data'),
    Output('DataTable', 'columns')],    
    [
        Input('upload-data', 'contents'),
        Input('upload-data', 'filename'),
        Input("x-variable", "value"),
        Input("y-variable", "value"),
        Input("ChecklistOptionsPeaks", "value"),
        Input("ChecklistOptionsMonth", "value"),    
        Input("ChecklistOptionsSum", "value"),    
        Input("slider_numberofmonths", "value"),    
        Input("inputqa", "value"),    
        Input('dataframevalue', 'data'),
        Input('dataframepeaksvalue', 'data'),
        Input('dataframepeaksvalueUseForDCA', 'data'),
        Input(component_id='Trinangular-left', component_property='value'),       
        Input(component_id='Trinangular-right', component_property='value'),       
        Input(component_id='Normal-std', component_property='value'),
        Input(component_id='prob-dist-button', component_property='value'),
        Input("ChecklistOptionsDeclineCurve", "value")]
)
def make_graph(icontents, ifilename,  xvalue, yvalue,ChecklistOptionsPeaks,ChecklistOptionsMonth,ChecklistOptionsSum,
               numberOfMonths,qa,dfvalue,dfPeaksvalue,dfPeaksvalueForDCA,
               triangularLeft,triangularRight,normalSTD,DistRadioButton,
               ChecklistOptionsDeclineCurve):
    P05Np=0
    P95Np=0
    meanNp=0
    
    data=[]
    TableData,TableCols=[],[]
    layout = {"xaxis": {"title": "X"}, "yaxis": {"title": "Y"}}
   
    
    fig = go.Figure()
    fig2 = go.Figure()
    fig3 = go.Figure()

    fig.update_layout(clickmode='event+select')

    yvalue=str(yvalue)
    yvalue=yvalue.replace('[','')
    yvalue=yvalue.replace(']','')
    yvalue=yvalue.replace("'",'')
    yvalue=yvalue.split(",")

    df = pd.DataFrame(columns=["Date"])
    dfPeaks = pd.DataFrame(columns=["Date"])
    
    df = df.set_index("Date")
    dfPeaks = dfPeaks.set_index("Date")
    # if contents:
    if icontents:
        for i,contents in enumerate(icontents):
            contents = icontents[i]
            filename = ifilename[i]
        
        df=pd.read_json(dfvalue, orient='split')
        dfPeaks=pd.read_json(dfPeaksvalue, orient='split')
        if dfPeaksvalueForDCA:
            dfPeaksForDCA=pd.read_json(dfPeaksvalueForDCA, orient='split')
        else:
            dfPeaksForDCA=pd.DataFrame(columns=["Date","ShowOnGraph"])
        tempmjd=df.reset_index()
        dfSelectedFields=tempmjd[xvalue]
        # dfSelectedFields=pd.concat([dfSelectedFields,dfPeaks['ShowOnGraph']],axis=1)
        

        # TableData,TableCols=df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
        dfTable=pd.concat([df.set_index(xvalue),dfPeaks.set_index(xvalue)],axis=1)
        # dfTable=dfTable.reset_index()
        
        for idx, yy in enumerate(yvalue):
            dfSelectedFields=pd.concat([dfSelectedFields,df[yy.strip()]],axis=1)
            tempdf=df.filter([xvalue,yy.strip()])
            tempdf.replace("", np.nan, inplace=True)
            tempdf.dropna(inplace=True)
            # tempdf=df
            fig.add_trace(
                    go.Scatter(
                        x=tempdf[xvalue],
                        y=tempdf[yy.strip()],
                        mode="markers",
                        marker={"size": 8},
                        yaxis='y1' ,
                        name=str(yy),
                    )) 
        if 'showTotal' in(ChecklistOptionsSum):
            dfSelectedFields['Total'] = dfSelectedFields.sum(axis=1)
            
            fig2.add_trace(
                    go.Scatter(
                        x=df[xvalue],
                        y=dfSelectedFields['Total'],
                        mode="markers",
                        marker={"size": 8,"color":"black", "symbol":"circle"},
                        yaxis='y1',
                        name="Total",
                    ))            
            indices = findPeaks(dfSelectedFields, 'Total', 1.0)
            sample_list = [contents, filename, dfSelectedFields,indices]
            # file_name = "GraphSelectedData.pkl"
            # open_file = open(file_name, "wb")
            # pickle.dump(sample_list, open_file)
            # open_file.close()
            dfPeaksTotal = dfSelectedFields.iloc[indices,:]
            dfPeaksTotal['ShowOnGraph']=True
            if dfPeaksForDCA.empty:
                dfPeaksForDCA=dfPeaksTotal.copy()

            
            dfPeaksTotal=dfPeaksTotal.reset_index()
            if 'showPeaks' in(ChecklistOptionsPeaks):       
                fig2.add_trace(
                    go.Scatter(
                        x=dfPeaksTotal[xvalue],
                        y=dfPeaksTotal['Total'],
                        mode="markers",
                        marker={"size": 8,"color":"red", "symbol":"diamond"},
                        yaxis='y1' ,
                        name=" Total Peaks",
                    ))

            sample_list = [dfSelectedFields,dfPeaksForDCA,dfPeaksTotal,df]
            file_name = "ArpesData.pkl"
            open_file = open(file_name, "wb")
            pickle.dump(sample_list, open_file)
            open_file.close()
                      
            mjddfPeaksTotalForDCA = pd.concat([df[xvalue],dfSelectedFields['Total'],dfPeaksForDCA['ShowOnGraph']], axis=1)
            dfPeaksTotalForDCA=mjddfPeaksTotalForDCA[mjddfPeaksTotalForDCA['ShowOnGraph'] ==True] 
            
            dfPeaksTotalForDCA=dfPeaksTotalForDCA.reset_index()
            if 'showPeaks' in(ChecklistOptionsPeaks):       
                fig2.add_trace(
                    go.Scatter(
                        x=dfPeaksTotalForDCA[xvalue],
                        y=dfPeaksTotalForDCA['Total'],
                        mode="markers",
                        marker={"size": 8,"color":"blue", "symbol":"square"},
                        yaxis='y1' ,
                        name=" DCA Peaks",
                    ))




            Arpesdf=pd.DataFrame()
            Duongdf=pd.DataFrame()
            

            if 'showArpes' in(ChecklistOptionsDeclineCurve): 
       
                dcayy={"Total"}
                for idx, yy in enumerate(dcayy):
                    '''
                    sample_list = [dfSelectedFields,dfPeaksTotalForDCA,xvalue,yy,qa,numberOfMonths,DistRadioButton]
                    file_name = "ArpesData.pkl"
                    open_file = open(file_name, "wb")
                    pickle.dump(sample_list, open_file)
                    open_file.close()
                    '''
                   
                    dfFitted,PeaksIndices,dfFittedLastPeak, t0, qi,b,Di=computeArpes(dfSelectedFields,dfPeaksTotalForDCA,xvalue,yy,qa,numberOfMonths,
                                                                                     int(triangularLeft),int(triangularRight),int(normalSTD),DistRadioButton)
                    Arpesdf=pd.DataFrame([[t0, qi,b,Di]], columns=['t0', 'qi','b','Di'])   
                    for mjd2idx,mjd2 in enumerate(PeaksIndices):
                      if mjd2idx==(len(PeaksIndices)-1):
                          fig3.add_trace(
                              go.Scatter(
                                  x=dfFittedLastPeak[xvalue],
                                  y=dfFittedLastPeak[yy.strip()+" (Arpes,Peak:"+str(mjd2idx)+")"],
                                  mode="lines",
                                  name=str(yy)+"Arpes"+str(mjd2idx+1)+")",
                              ))
                          fig3.add_trace(
                              go.Scatter(
                                  x=dfFittedLastPeak[xvalue],
                                  y=dfFittedLastPeak[yy.strip()+"ArpesP95"],
                                  mode="lines",
                                  fill=None,
                                  name=str(yy)+"ArpesP95",
                              ))
                          fig3.add_trace(
                              go.Scatter(
                                  x=dfFittedLastPeak[xvalue],
                                  y=dfFittedLastPeak[yy.strip()+"ArpesP05"],
                                  mode="lines",
                                  fill="tonexty",
                                  name=str(yy)+"ArpesP05",
                              ))
                      
                  
                      fig2.add_trace(
                          go.Scatter(
                              x=dfFitted[xvalue],
                              y=dfFitted[yy.strip()+" (Arpes,Peak:"+str(mjd2idx)+")"],
                              mode="lines",
                              yaxis='y1' ,
                              name=str(yy)+" (Arpes,Peak:"+")",
                          ))
    

                dfFitted=dfFitted.set_index(xvalue)
                dfTable=pd.concat([dfTable,dfFitted],axis=1,join='outer')
    
            if 'showDuong' in(ChecklistOptionsDeclineCurve):       
                dcayy={"Total"}
                for idx, yy in enumerate(dcayy):
                    dfFitted,PeaksIndices,dfFittedLastPeak,t0, q1,q_inf, a, m=computeDuong(dfSelectedFields,dfPeaksTotalForDCA,xvalue,yy,qa,numberOfMonths,
                                                                                           int(triangularLeft),int(triangularRight),int(normalSTD),DistRadioButton)
                    Duongdf=pd.DataFrame([[t0, q1,q_inf, a, m]],columns=['t0', 'q1','q_inf', 'a', 'm'])              
                    '''
                    sample_list = [dfFitted,PeaksIndices,dfFittedLastPeak]
                    file_name = "ArpesData.pkl"
                    open_file = open(file_name, "wb")
                    pickle.dump(sample_list, open_file)
                    open_file.close()
                    '''                
                    for mjd2idx,mjd2 in enumerate(PeaksIndices):
                        if mjd2idx==(len(PeaksIndices)-1):
                            fig3.add_trace(
                                go.Scatter(
                                    x=dfFittedLastPeak[xvalue],
                                    y=dfFittedLastPeak[yy.strip()+" (Duong,Peak:"+str(mjd2idx)+")"],
                                    mode="lines",
                                    name=str(yy)+"Duong"+str(mjd2idx+1)+")",
                                ))
                            fig3.add_trace(
                                go.Scatter(
                                    x=dfFittedLastPeak[xvalue],
                                    y=dfFittedLastPeak["DuongP95"],
                                    mode="lines",
                                    fill=None,
                                    name=str(yy)+"DuongP95",
                                ))
                            fig3.add_trace(
                                go.Scatter(
                                    x=dfFittedLastPeak[xvalue],
                                    y=dfFittedLastPeak["DuongP05"],
                                    mode="lines",
                                    fill="tonexty",
                                    name=str(yy)+"DuongP05",
                                ))
                            
                        
                        fig2.add_trace(
                            go.Scatter(
                                x=dfFitted[xvalue],
                                y=dfFitted[yy.strip()+" (Duong,Peak:"+str(mjd2idx)+")"],
                                mode="lines",
                                yaxis='y1' ,
                                name=str(yy)+" (Duong,Peak:"+")",
                            ))
                dfFitted=dfFitted.set_index(xvalue)
                dfTable=pd.concat([dfTable,dfFitted],axis=1,join='outer')

                    

        
        fig['layout'] = go.Layout( {"xaxis": {"title": xvalue} })
        fig2['layout'] = go.Layout( {"title":"Data for DCA","xaxis": {"title": xvalue}, "yaxis": {"title":"total sum","overlaying": "y1"}})
        fig3['layout'] = go.Layout( {"title":"Confidence Interval","xaxis": {"title": xvalue}, "yaxis": {"title":"","overlaying": "y1"}})
                
        dfTable=dfTable.reset_index()
        dfTable['index'] = np.arange(1, len(dfTable)+1)
        dfTable = dfTable.loc[:,~dfTable.columns.duplicated()]
        TableData,TableCols=dfTable.to_dict('records'), [{"name": i, "id": i} for i in dfTable.columns]    
    # return 'Cumulative production Np= {:1f}, 90% confidence {:1f} - {:1f}'.format(meanNp, P95Np, P05Np) ,  fig,fig2,TableData,TableCols #go.Figure(data=data, layout=layout)
    # strg=" Np= {:.1f}, 90% confidence {:.1f} - {:.1f}".format(meanNp, P95Np, P05Np)
    strg=" Np= {:.0f}, 90% confidence {:.0f} - {:.0f}".format(float(meanNp), float(P05Np), float(P95Np))
    fig.update_layout(
        legend=dict(
            x=1.5,
            y=0,
            traceorder="normal",
            xanchor="left",
            yanchor="top",
        )
    )
    fig2.update_layout(
        clickmode='event+select'
    )

    return json.dumps(Arpesdf.to_json(date_format='iso',orient='split'), indent=2),       strg ,  fig,fig2,fig3,TableData,TableCols 


#------------------------------------------------------------------------------
#---------------------PARSE _ DATA---------------------------------------------
#------------------------------------------------------------------------------
def parse_data(contents, filename, ChecklistOptionsMonth):
    try:
        print(f"Parsing file: {filename}")

        # Decode the uploaded content
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        # Load file based on extension
        if filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(decoded))
        elif filename.endswith((".txt", ".tsv")):
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), delimiter=r"\s+")
        else:
            raise ValueError("Unsupported file type")

        # Clean empty values
        df.replace({0: np.nan, r'^\s*$': np.nan}, regex=True, inplace=True)
        df.dropna(axis='columns', how='all', inplace=True)

        # Add filename prefix to columns (for uniqueness)
        df.columns = [f"{filename} : {col}" for col in df.columns]

        # Detect and parse datetime columns
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

        datetime_cols = df.select_dtypes(include=["datetime64[ns]"])
        if datetime_cols.empty:
            raise ValueError("No valid datetime column found.")

        # Rename the first datetime column to 'Date'
        date_col = datetime_cols.columns[0]
        df.rename(columns={date_col: "Date"}, inplace=True)
        date_col = "Date"

        # Resample by month if specified
        if 'Month' in ChecklistOptionsMonth:
            df.set_index(date_col, inplace=True)
            df = df.resample("MS").mean().reset_index()

        # Prepare peaks DataFrame
        dfPeaks = pd.DataFrame(df[date_col])

        for col in df.columns:
            if col == date_col or df[col].isnull().all():
                continue

            df = removeMinima(df, col, 1.2)
            # df = fillMissingDates(df, date_col) # Uncomment if you want to fill missing dates
            df = removeOutliers(df, col, 3.5)
            df = fillMissingDates(df, date_col)

            peaks_idx = findPeaks(df, col, 1.0)
            peaks_data = df[[col]].iloc[peaks_idx]
            dfPeaks = pd.concat([dfPeaks, peaks_data], axis=1)

        return df.reset_index(drop=True), dfPeaks.reset_index(drop=True), date_col

    except Exception as e:
        print(f"❌ Error while parsing data: {e}")
        return None, None, None
    
    
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def computeArpes(df,dfPeaks,xvalue,yy,qa,numberOfMonths,triangularLeft,triangularRight,normalSTD,DistRadioButton):
    dfArpes = pd.DataFrame([])
    # for idx, yy in enumerate(yvalue):
    dfFit= pd.concat([dfPeaks[xvalue],dfPeaks[yy]],axis=1)
    dfFit=df[df.Date.isin(dfPeaks.Date)]
    PeaksIndices=dfFit[~dfFit[yy].isnull()].index.tolist()
    dfFit=pd.concat([df[xvalue],df[yy]],axis=1)
                    
    for mjd2idx,mjd2 in enumerate(PeaksIndices):
        dfFitted, x,t0, qi,b,Di=fitArpsModel(dfFit,PeaksIndices,mjd2idx,numberOfMonths)
        if mjd2idx==(len(PeaksIndices)-1):
            dfFitted , P05Np, P95Np, meanNp=MonteCarloSimulationArpes(dfFitted, x,t0, qi,b,Di,numberOfMonths,qa,yy,
                                                                      triangularLeft,triangularRight,normalSTD,DistRadioButton)
            dfFittedLastPeak=dfFitted
            tempdfFitted=dfFitted.filter([xvalue,yy])
            tempdfFitted.replace("", np.nan, inplace=True)
            tempdfFitted.dropna(inplace=True)
        dfFitted1=dfFitted.set_index(xvalue)
        dfFitted1=dfFitted1.rename(columns={yy: yy+" (Arpes,Peak:"+str(mjd2idx)+")"})
        dfArpes=pd.concat([dfArpes,dfFitted1],axis=1,join='outer')
        
    dfFittedLastPeak=dfFittedLastPeak.set_index(xvalue)
    dfFittedLastPeak=dfFittedLastPeak.rename(columns={yy: yy+" (Arpes,Peak:"+str(mjd2idx)+")"})
    dfFittedLastPeak=dfFittedLastPeak.reset_index()

    
    dfArpes.replace("", np.nan, inplace=True)
    # dfArpes.dropna(inplace=True)        
    # dfArpes=dfArpes.set_index(xvalue)
    dfArpes=dfArpes.reset_index()
       
    return dfArpes,PeaksIndices,dfFittedLastPeak, t0, qi,b,Di
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def computeDuong(df,dfPeaks,xvalue,yy,qa,numberOfMonths,triangularLeft,triangularRight,normalSTD,DistRadioButton):
    dfDuong = pd.DataFrame([])
    # for idx, yy in enumerate(yvalue):
    dfFit= pd.concat([dfPeaks[xvalue],dfPeaks[yy]],axis=1)
    dfFit=df[df.Date.isin(dfPeaks.Date)]
    PeaksIndices=dfFit[~dfFit[yy].isnull()].index.tolist()
    dfFit=pd.concat([df[xvalue],df[yy]],axis=1)
                    
    for mjd2idx,mjd2 in enumerate(PeaksIndices):
        dfFitted,x,t0, q1,q_inf, a, m=fitDuongModel(dfFit,PeaksIndices,mjd2idx,numberOfMonths)

        # dfFitted, x,t0, qi,b,Di=fitArpsModel(dfFit,PeaksIndices,mjd2idx,numberOfMonths)
        if mjd2idx==(len(PeaksIndices)-1):
            dfFitted , P05Np, P95Np, meanNp=MonteCarloSimulationDuong(dfFitted, x,t0, q1,q_inf, a, m,numberOfMonths,qa,
                                                                      triangularLeft,triangularRight,normalSTD,DistRadioButton)
            # dfFitted , P05Np, P95Np, meanNp=MonteCarloSimulationArpes(dfFitted, x,t0, qi,b,Di,numberOfMonths,qa,yy)
            dfFittedLastPeak=dfFitted
            tempdfFitted=dfFitted.filter([xvalue,yy])
            tempdfFitted.replace("", np.nan, inplace=True)
            tempdfFitted.dropna(inplace=True)
        dfFitted1=dfFitted.set_index(xvalue)
        dfFitted1=dfFitted1.rename(columns={yy: yy+" (Duong,Peak:"+str(mjd2idx)+")"})
        dfDuong=pd.concat([dfDuong,dfFitted1],axis=1,join='outer')
        
    dfFittedLastPeak=dfFittedLastPeak.set_index(xvalue)
    dfFittedLastPeak=dfFittedLastPeak.rename(columns={yy: yy+" (Duong,Peak:"+str(mjd2idx)+")"})
    dfFittedLastPeak=dfFittedLastPeak.reset_index()

    
    dfDuong.replace("", np.nan, inplace=True)
    # dfArpes.dropna(inplace=True)        
    # dfArpes=dfArpes.set_index(xvalue)
    dfDuong=dfDuong.reset_index()
       
    return dfDuong,PeaksIndices,dfFittedLastPeak,t0, q1,q_inf, a, m
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

if __name__ == "__main__":
    # app.run_server(debug=True, port=8888)
    app.run_server()