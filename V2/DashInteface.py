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
import json
from datetime import date
from dash import Input, Output, State, html, dcc, callback, exceptions
import time

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from V2.DCA04 import *


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
                    options=[],
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

        # Toggle and range for peaks display
        dbc.Row([
            dbc.Col([
                dbc.Checkbox(
                    id="show-peaks-toggle",
                    value=True,
                ),
                html.Label("show peaks", htmlFor="show-peaks-toggle", style={"marginLeft": "8px"}),
            ])
        ], className="mb-3"),

        html.Div([
        html.Label("Select Peaks Date Range", className="fw-bold"),
        dcc.DatePickerRange(
            id='peaks-date-range',
            display_format='YYYY-MM-DD',
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date",
            style={"marginBottom": "10px"}
        )
        ], style={"marginTop": "10px"})
    ],
    body=True,
    color="#F9F9F9",
    className="shadow-sm"
)

declineCurveAnalysis = dbc.Card(
    dbc.CardBody([

        # --- Title ---
        html.H5("Decline Curve Analysis", className="card-title mb-3"),

        # --- Model Selector ---
        dbc.Row([
            dbc.Col(html.Label("Select DCA Model(s):"), width="auto"),
            dbc.Col(
                dcc.Checklist(
                    id="dca-model-selector",
                    options=[
                        {"label": "Hyperbolic", "value": "hyperbolic"},
                        {"label": "Exponential", "value": "exponential"},
                        {"label": "Harmonic", "value": "harmonic"},
                        {"label": "Duong", "value": "duong"},
                        {"label": "Arps", "value": "arps"},
                        {"label": "Show Total", "value": "total"},
                    ],
                    value=["hyperbolic"],
                    inline=True,
                    labelStyle={"marginRight": "15px"}
                ),
                width="auto"
            )
        ], className="mb-3 align-items-center"),

        dbc.Row([
            dbc.Col([
                html.Label("Select Row Count:"),
                dcc.Slider(
                    id="dca-row-slider",
                    min=10,
                    max=5000, 
                    step=10,      
                    value=100,     
                    marks={i: str(i) for i in range(100, 5001, 1000)},  
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], width=12),
        ], className="mb-3"),


        # --- Date Picker & Column Selector ---
        dbc.Row([
            dbc.Col([
                html.Label("Date Range:"),
                dcc.DatePickerRange(
                    id='dca-date-range',
                    min_date_allowed=date(2000, 1, 1),
                    max_date_allowed=date(2100, 1, 1),
                    start_date=date(2000, 1, 1),
                    end_date=date(2020, 1, 1),
                    display_format='YYYY-MM-DD',
                )
            ], width=5),

            dbc.Col([
                html.Label("Select Column:"),
                dcc.Dropdown(
                    id="dca-column-dropdown",
                    placeholder="Select rate column..."
                )
            ], width=7),
        ], className="mb-3"),


        # --- Run Button ---
        dbc.Row([
            dbc.Col(
                dbc.Button("Run DCA", id="run-dca-btn", color="primary", className="w-100"),
                width=3
            )
        ], justify="start", className="mb-4"),

        # --- Graph ---
        dcc.Graph(id="dca-graph", style={"height": "400px"}),

        # --- Results Section ---
        html.Div(id="dca-results", className="mt-3"),

    ]),
    className="mt-3 border border-primary-subtle",
    style={"backgroundColor": "#ffffff", "padding": "10px", "borderRadius": "6px"}
)

monteCarloSimulation = dbc.Card(
    dbc.CardBody([

        html.H5("Monte Carlo Simulation", className="card-title"),

        dbc.Row([

            dbc.Col([
                dbc.Label("Iterations"),
                dcc.Input(
                    id="mc-iterations",
                    type="number",
                    value=500,
                    min=100,
                    step=100,
                    debounce=True,
                    className="form-control"
                )
            ], md=6),

            dbc.Col([
                dbc.Label("Uncertainty Scale"),
                dcc.Slider(
                    id="mc-uncertainty",
                    min=0.5,
                    max=2.0,
                    step=0.1,
                    value=1.0,
                    marks={
                        0.5: "Low",
                        1.0: "Base",
                        1.5: "High",
                        2.0: "Stress"
                    },
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], md=6),

        ], className="mb-3"),

        html.Div("Uncertainty scale multiplies the base parameter standard deviations.", 
                 className="text-muted small mb-2"),

        dcc.Store(id="dca-params-store"),
        dcc.Store(id="dca-time-array"),

        dbc.Button(
            "Run Monte Carlo",
            id="run-monte-carlo-btn",
            n_clicks=0,
            color="success",
            className="mb-3"
        ),

        dcc.Graph(id="monte-carlo-graph")

    ]),
    className="mt-3 border border-success-subtle",
    style={
        "backgroundColor": "#f8f9fa",
        "padding": "12px",
        "borderRadius": "8px"
    }
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
                                dcc.Store(id="dca-parameters"),
                                dcc.Store(id="dca-time-array"),

                                dbc.Row(
                                    [
                                        dbc.Col(uploadSection, md=12),
                                    ],
                                    className="mb-4"
                                ),

                                dbc.Row(
                                    [
                                        dbc.Col(declineCurveAnalysis, md=12),
                                    ],
                                    className="mb-4"
                                ),

                                
                                dbc.Row(
                                    [
                                        dbc.Col(monteCarloSimulation, md=12),
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
def update_checklist(icontents, ifilename, date):
    dff = pd.DataFrame(columns=["Date"]).set_index("Date")
    dffPeaks = pd.DataFrame(columns=["Date"]).set_index("Date")   

    if icontents:
        for i, contents in enumerate(icontents):
            filename = ifilename[i]

            df1, dfPeaks1, dateCol = parse_data(contents, filename, [''])

            df1 = df1.set_index(dateCol)
            dfPeaks1 = dfPeaks1.set_index(dateCol)
    
            dff = pd.concat([dff, df1], axis=1)
            dffPeaks = pd.concat([dffPeaks, dfPeaks1], axis=1)
        
        dffPeaks['ShowOnGraph'] = False    

        if "index" in dff.columns:
            dff.drop("index", axis=1, inplace=True)
        if "index" in dffPeaks.columns:
            dffPeaks.drop("index", axis=1, inplace=True) 

        dff = dff.reset_index()
        dffPeaks = dffPeaks.reset_index()

    checklist_options = [
        {"label": col, "value": col}
        for col in dff.columns.to_list()
        if col != dateCol
    ]

    return [
        checklist_options,
        dff.to_json(date_format='iso', orient='split'),
        dffPeaks.to_json(date_format='iso', orient='split')
    ]

@app.callback(
    Output("data-preview-graph", "figure"),
    [
        Input("checklistfiles", "value"),
        Input("dataframevalue", "data"),
        Input("dataframepeaksvalue", "data"),
        Input("show-peaks-toggle", "checked"),
        Input("peaks-date-range", "start_date"),
        Input("peaks-date-range", "end_date")
    ],
    prevent_initial_call=True
)
def update_graph(selected_columns, df_json, peaks_json, show_peaks, start_date, end_date):
    if not selected_columns or not df_json or not peaks_json:
        fig = go.Figure()
        fig.update_layout(
            title="No data to display",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[dict(
                text="Please upload data and select columns to display the graph.",
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=16)
            )],
            template="plotly_white"
        )
        return fig

    df = pd.read_json(df_json, orient="split")
    df_peaks = pd.read_json(peaks_json, orient="split")

    # اگر تاریخ شروع یا پایان مشخص شده، فیلتر کن
    if start_date:
        df_peaks = df_peaks[df_peaks['Date'] >= start_date]
    if end_date:
        df_peaks = df_peaks[df_peaks['Date'] <= end_date]

    fig = go.Figure()

    for col in selected_columns:
        if col not in df.columns:
            continue

        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df[col],
            mode='lines+markers',
            name=col,
            line=dict(width=2),
            marker=dict(size=6),
            hovertemplate='%{x|%Y-%m-%d %H:%M:%S}<br>%{y}<extra>' + col + '</extra>'
        ))

        if show_peaks and col in df_peaks.columns:
            fig.add_trace(go.Scatter(
                x=df_peaks['Date'],
                y=df_peaks[col],
                mode='markers',
                name=f"Peaks - {col}",
                marker=dict(color='red', size=8, symbol='circle'),
                showlegend=True
            ))

    fig.update_layout(
        title=dict(
            text="Selected Data Columns",
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        xaxis=dict(
            title="Date",
            showgrid=True,
            zeroline=False,
            showline=True,
            linewidth=1,
            linecolor='black',
            mirror=True,
            tickformat='%Y-%m-%d',
            rangeslider=dict(visible=True),
            type='date'
        ),
        yaxis=dict(
            title="Values",
            showgrid=True,
            zeroline=False,
            showline=True,
            linewidth=1,
            linecolor='black',
            mirror=True,
        ),
        legend=dict(
            title="Columns",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template="plotly_white",
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50),
        dragmode='zoom'
    )

    return fig

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

@app.callback(
    Output("dca-column-dropdown", "options"),
    Input("checklistfiles", "options")
)
def sync_dropdown_with_checklist(checklist_options):
    return checklist_options

def hyperbolic_decline(t, qi, Di, b):
    return qi / np.power(1 + b * Di * t, 1 / b)

def exponential_decline(t, qi, Di):
    return qi * np.exp(-Di * t)

def harmonic_decline(t, qi, Di):
    return qi / (1 + Di * t)

def arps_decline(t, qi, Di, b):
    """
    Arps decline curve model
    q(t) = qi / (1 + b * Di * t)^(1/b)
    """
    return qi / np.power(1 + b * Di * t, 1 / b)


def duong_decline(t, qi, a, m):
    """
    Duong decline curve model
    q(t) = qi / (t+1)^m * exp(-a * (t))
    """
    t = np.array(t, dtype=float)
    return qi / np.power(t + 1, m) * np.exp(-a * t)

@app.callback(
    [Output("dca-graph", "figure"),
     Output("dca-results", "children"),
     Output("dca-params-store", "data"),
     Output("dca-time-array", "data")],
    Input("run-dca-btn", "n_clicks"),
    State("dca-column-dropdown", "value"),
    State("dca-model-selector", "value"),
    State("dca-row-slider", "value"),
    State("dataframevalue", "data"),
    State("dca-date-range", "start_date"),
    State("dca-date-range", "end_date"),
    prevent_initial_call=True
)
def run_dca_model(n_clicks, column, model_types, row_limit, df_json, start_date, end_date):
    if not column or not df_json or not model_types:
        raise exceptions.PreventUpdate

    try:
        df = pd.read_json(df_json, orient='split')
        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
        df = df.dropna(subset=[column])
        df = df.sort_values("Date")

        if start_date and end_date:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

            df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

        if row_limit:
            df = df.head(row_limit)

        if df.empty:
            return go.Figure(), html.Div("❌ No data in selected date range."), {}, []

        # calculate time in days from the first date
        t = (df["Date"] - df["Date"].iloc[0]).dt.days.values
        q = df[column].values

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Date"], y=q, mode="markers", name="Actual Data"))

        results_blocks = []
        params_store = {}
        total_curve = np.zeros_like(q, dtype=float)

        for model_type in model_types:
            if model_type == "exponential":
                func = exponential_decline
                p0 = [q[0], 0.01]
            elif model_type == "harmonic":
                func = harmonic_decline
                p0 = [q[0], 0.01]
            elif model_type == "hyperbolic":
                func = hyperbolic_decline
                p0 = [q[0], 0.01, 0.5]
            elif model_type == "duong":
                func = duong_decline
                p0 = [q[0], 0.001, 0.5]

            elif model_type == "arps":
                func = arps_decline
                p0 = [q[0], 0.01, 0.5]
            elif model_type == "total":
                continue
            else:
                continue

            try:
                params, _ = curve_fit(func, t, q, p0=p0, maxfev=10000)
                q_fit = func(t, *params)

                total_curve += q_fit

                fig.add_trace(go.Scatter(
                    x=df["Date"], y=q_fit, mode="lines",
                    name=f"{model_type.title()} Fit"
                ))

                result_text = f"### {model_type.title()} Decline Parameters\n"
                if model_type == "hyperbolic":
                    qi, Di, b = params
                    params_store[model_type] = {"qi": float(qi), "Di": float(Di), "b": float(b)}
                    result_text += f"- qi = {qi:.2f}\n- Di = {Di:.4f} /day\n- b = {b:.2f}\n"
                else:
                    qi, Di = params[:2]
                    params_store[model_type] = {"qi": float(qi), "Di": float(Di), "b": None}
                    result_text += f"- qi = {qi:.2f}\n- Di = {Di:.4f} /day\n"

                results_blocks.append(dcc.Markdown(result_text))

            except Exception as e:
                results_blocks.append(html.Div(f"❌ Error fitting {model_type}: {e}"))

        if "total" in model_types:
            fig.add_trace(go.Scatter(
                x=df["Date"], y=total_curve, mode="lines", name="Total Fit", line=dict(dash="dot", width=3)
            ))
            results_blocks.append(dcc.Markdown("### Total Curve\n✅ Sum of all selected models"))

        fig.update_layout(
            title=f"Decline Curve Analysis - {column}",
            xaxis_title="Date",
            yaxis_title="Rate",
            template="plotly_white"
        )
        
        print("Start:", start_date, "End:", end_date)
        print("Remaining rows:", len(df))

        return fig, results_blocks, params_store, t.tolist()

    except Exception as e:
        return go.Figure(), html.Div(f"❌ Error fitting model: {e}"), {}, []
    
@app.callback(
    [Output("debug-params", "children"),
     Output("debug-time", "children")],
    [Input("dca-params-store", "data"),
     Input("dca-time-array", "data")]
)
def debug_outputs(params, time_array):
    return str(params), str(time_array)

def create_monte_carlo_figure(results):

    n_iter, t_max = results.shape
    t = np.arange(1, t_max + 1)

    fig = go.Figure()

    for i in range(n_iter):
        fig.add_trace(go.Scatter(
            x=t,
            y=results[i, :],
            mode='lines',
            line=dict(width=1, color='rgba(0,0,255,0.1)'),
            showlegend=False
        ))

    mean_curve = np.mean(results, axis=0)
    fig.add_trace(go.Scatter(
        x=t,
        y=mean_curve,
        mode='lines',
        line=dict(width=3, color='blue'),
        name='Mean'
    ))

    fig.update_layout(
        title="Monte Carlo Simulation Results",
        xaxis_title="Time (months)",
        yaxis_title="Production Rate",
        template="plotly_white",
        height=400
    )
    return fig

@app.callback(
    Output("monte-carlo-graph", "figure"),
    Input("run-monte-carlo-btn", "n_clicks"),
    State("dca-params-store", "data"),
    State("dca-model-selector", "value"),
    State("dca-time-array", "data"),
    State("mc-iterations", "value"),
    State("mc-uncertainty", "value"),
    prevent_initial_call=True
)
def run_monte_carlo(n_clicks, params_store, model_types, t_array, n_simulations, uncertainty_scale):

    if not params_store or not t_array or not model_types:
        raise exceptions.PreventUpdate

    import numpy as np
    import plotly.graph_objects as go

    # pick first non-total model
    model_type = next((m for m in model_types if m != "total"), None)
    if model_type not in params_store:
        raise exceptions.PreventUpdate

    params = params_store[model_type]

    t = np.array(t_array)

    n_simulations = int(n_simulations or 500)
    uncertainty_scale = float(uncertainty_scale or 1.0)

    qi_mu = params["qi"]
    Di_mu = params["Di"]
    b_mu  = params.get("b")

    qi_sigma = 0.05 * qi_mu * uncertainty_scale
    Di_sigma = 0.10 * Di_mu * uncertainty_scale
    b_sigma  = 0.15 * b_mu  * uncertainty_scale if b_mu is not None else None

    simulations = []

    for _ in range(n_simulations):

        qi = np.random.normal(qi_mu, qi_sigma)
        Di = np.random.normal(Di_mu, Di_sigma)
        b  = np.random.normal(b_mu, b_sigma) if b_mu is not None else None

        qi = np.clip(qi, 1e-6, None)
        Di = np.clip(Di, 1e-6, 10.0)
        if b is not None:
            b = np.clip(b, 0.05, 2.0)

        if model_type == "exponential":
            q_sim = qi * np.exp(-Di * t)
        elif model_type == "harmonic":
            q_sim = qi / (1 + Di * t)
        elif model_type == "hyperbolic":
            q_sim = qi / np.power(1 + b * Di * t, 1 / b)
        elif model_type == "duong":
            q_sim = qi * np.exp(-Di * t) * np.power(t + 1, -b)
        elif model_type == "arps":
            q_sim = qi / np.power(1 + b * Di * t, 1 / b)
        else:
            raise exceptions.PreventUpdate

        simulations.append(q_sim)

    fig = go.Figure()

    for sim in simulations:
        fig.add_trace(go.Scatter(
            x=t,
            y=sim,
            mode="lines",
            line=dict(width=1),
            opacity=0.12,
            showlegend=False
        ))

    fig.update_layout(
        title=f"Monte Carlo Simulation ({model_type.title()})",
        xaxis_title="Time (days)",
        yaxis_title="Rate",
        template="plotly_white"
    )

    return fig

if __name__ == "__main__":
    app.run()