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

from dca_pes.DCA04 import *


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
                html.Label("Select Column(s):"),
                dcc.Dropdown(
                    id="dca-column-dropdown",
                    placeholder="Select rate column(s)...",
                    multi=True
                )
            ], width=7),
        ], className="mb-3"),

        dbc.Row([
            dbc.Col(dbc.Switch(id="show-cumulative-toggle", label="Show cumulative on main graph", value=False), md=4),
            dbc.Col(dbc.Switch(id="show-cumulative-view", label="Show cumulative-only view", value=False), md=4),
        ]),

        # --- Graph ---
        dcc.Graph(id="dca-graph", style={"height": "400px"}),
        dcc.Graph(id="cumulative-graph"),

        # --- Results Section ---
        html.Div(id="dca-results", className="mt-3"),

        # --- Export ---
        dbc.Row([
            dbc.Col(
                dbc.Button("Export CSV", id="export-dca-csv-btn", color="secondary",
                           outline=True, className="w-100"),
                width=3
            ),
            dbc.Col(
                dbc.Button("Export Excel", id="export-dca-excel-btn", color="secondary",
                           outline=True, className="w-100"),
                width=3
            ),
        ], className="mt-3 g-2"),
        dcc.Download(id="dca-download-csv"),
        dcc.Download(id="dca-download-excel"),

    ]),
    className="mt-3 border border-primary-subtle",
    style={"backgroundColor": "#ffffff", "padding": "10px", "borderRadius": "6px"}
)

monteCarloSimulation = dbc.Card(
    dbc.CardBody([

        html.H5("Monte Carlo Simulation", className="card-title"),

        dbc.Row([
            dbc.Col([
                dbc.Label("Fit to simulate"),
                dcc.Dropdown(
                    id="mc-fit-selector",
                    placeholder="Run a DCA fit above first...",
                )
            ], md=12),
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                dbc.Label("Economic Limit (q min)"),
                dcc.Input(id="mc-q-min", type="number", value=1.0, step=0.1, className="form-control")
            ], md=6),

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
        ], className="mb-3"),

        html.H6("Per-Parameter Uncertainty (\u00b1 % around the fitted value)", className="fw-bold mt-2"),

        dbc.Row([
            dbc.Col([
                dbc.Label("qi uncertainty (%)"),
                dcc.Slider(
                    id="mc-qi-uncertainty",
                    min=0, max=100, step=1, value=5,
                    marks={0: "0%", 25: "25%", 50: "50%", 75: "75%", 100: "100%"},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], md=4),

            dbc.Col([
                dbc.Label("Di uncertainty (%)"),
                dcc.Slider(
                    id="mc-di-uncertainty",
                    min=0, max=100, step=1, value=10,
                    marks={0: "0%", 25: "25%", 50: "50%", 75: "75%", 100: "100%"},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], md=4),

            dbc.Col([
                dbc.Label("b uncertainty (%)"),
                dcc.Slider(
                    id="mc-b-uncertainty",
                    min=0, max=100, step=1, value=15,
                    marks={0: "0%", 25: "25%", 50: "50%", 75: "75%", 100: "100%"},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], md=4),
        ], className="mb-2"),

        html.Div("Each slider sets that parameter's own spread (as a % of its fitted value) used to sample the Monte Carlo runs. "
                 "b uncertainty only affects models with a b parameter (Hyperbolic, Arps).",
                 className="text-muted small mb-2"),

        dbc.Row([
            dbc.Col([
                dbc.Label("Di \u2194 b correlation"),
                dcc.Slider(
                    id="mc-di-b-correlation",
                    min=-0.95, max=0.95, step=0.05, value=0.0,
                    marks={-0.95: "-0.95", -0.5: "-0.5", 0: "0", 0.5: "0.5", 0.95: "0.95"},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], md=8),
        ], className="mb-2"),

        html.Div("Controls whether Di and b are sampled independently (0) or move together: positive values mean "
                 "high-Di draws tend to pair with high-b draws, negative values mean they move oppositely. "
                 "Only applies to models with a b parameter (Hyperbolic, Arps).",
                 className="text-muted small mb-2"),

        dbc.Checklist(
            id="mc-show-actual",
            options=[{"label": "Show original data on Monte Carlo chart", "value": "show"}],
            value=["show"],
            switch=True,
            className="mb-2"
        ),

        dcc.Store(id="dca-params-store"),
        dcc.Store(id="dca-time-array"),
        dcc.Store(id="dca-actual-data"),
        dcc.Store(id="dca-export-store"),

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

            if df1 is None or dateCol is None:
                print(f"Skipping '{filename}': could not be parsed (see error above).")
                continue

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
        if col != "Date"
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

    df = pd.read_json(io.StringIO(df_json), orient="split")
    df_peaks = pd.read_json(io.StringIO(peaks_json), orient="split")

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

        # Detect and parse datetime columns. Check is dtype-agnostic (not 'object'-only)
        # because pandas 3.x defaults text columns to a dedicated 'str' dtype rather than
        # 'object', which would otherwise make this loop skip every text column entirely.
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
                continue
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
     Output("cumulative-graph", "figure"),
     Output("dca-results", "children"),
     Output("dca-params-store", "data"),
     Output("dca-time-array", "data"),
     Output("dca-actual-data", "data"),
     Output("dca-export-store", "data")],
    Input("dca-column-dropdown", "value"),
    Input("dca-model-selector", "value"),
    Input("dca-row-slider", "value"),
    Input("dataframevalue", "data"),
    Input("dca-date-range", "start_date"),
    Input("dca-date-range", "end_date"),
    Input("show-cumulative-toggle", "value"),
    Input("show-cumulative-view", "value"),
    prevent_initial_call=True
)
def run_dca_model(columns, model_types, row_limit, df_json,
                  start_date, end_date, show_cum_on_rate, show_cum_view):
    if not columns or not df_json or not model_types:
        raise exceptions.PreventUpdate

    if isinstance(columns, str):
        columns = [columns]

    df_full = pd.read_json(io.StringIO(df_json), orient="split")
    df_full["Date"] = pd.to_datetime(df_full["Date"]).dt.tz_localize(None)

    if start_date and end_date:
        df_full = df_full[(df_full["Date"] >= pd.to_datetime(start_date)) & (df_full["Date"] <= pd.to_datetime(end_date))]

    fig_rate = go.Figure()
    fig_cum = go.Figure()
    results_blocks = []
    params_store = {}
    actual_data_store = {}
    export_rows = []
    last_t = []

    # A distinct color per column so every model fitted to the same column shares
    # a color family, making cross-column comparison readable at a glance.
    palette = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf", "#e377c2", "#8c564b"]

    for col_idx, column in enumerate(columns):
        color = palette[col_idx % len(palette)]

        df = df_full.dropna(subset=[column]).sort_values("Date")
        if row_limit:
            df = df.head(row_limit)
        if df.empty:
            continue

        t = (df["Date"] - df["Date"].iloc[0]).dt.days.values
        q = df[column].values
        dt = np.diff(t, prepend=t[0])
        dt[dt <= 0] = 1.0
        last_t = t.tolist()

        fig_rate.add_trace(go.Scatter(
            x=df["Date"], y=q, mode="markers", name=f"{column} (actual)",
            marker=dict(color=color, size=5)
        ))

        date_strs = df["Date"].dt.strftime("%Y-%m-%d").tolist()

        col_params = {}
        total_curve = np.zeros_like(q, dtype=float)
        col_results = []

        for model_type in model_types:
            if model_type == "exponential":
                func, p0 = exponential_decline, [q[0], 0.01]
            elif model_type == "harmonic":
                func, p0 = harmonic_decline, [q[0], 0.01]
            elif model_type == "hyperbolic":
                func, p0 = hyperbolic_decline, [q[0], 0.01, 0.5]
            elif model_type == "duong":
                func, p0 = duong_decline, [q[0], 0.001, 0.5]
            elif model_type == "arps":
                func, p0 = arps_decline, [q[0], 0.01, 0.5]
            elif model_type == "total":
                continue
            else:
                continue

            try:
                params, _ = curve_fit(func, t, q, p0=p0, maxfev=10000)
            except RuntimeError as e:
                col_results.append(dcc.Markdown(f"### {column} \u2014 {model_type.title()}\n_Fit failed: {e}_"))
                continue

            q_fit = func(t, *params)
            Q_cum = np.cumsum(q_fit * dt)
            total_curve += q_fit

            resid = q - q_fit
            n_pts, n_params = len(t), len(params)
            dof = max(n_pts - n_params, 1)  # degrees of freedom, floored at 1 to avoid div-by-zero on tiny samples

            rmse = float(np.sqrt(np.mean(resid ** 2)))
            mae = float(np.mean(np.abs(resid)))
            std_error = float(np.sqrt(np.sum(resid ** 2) / dof))  # standard error of the regression (dof-corrected)
            rmse_pct = float(rmse / np.mean(q) * 100) if np.mean(q) != 0 else None

            nonzero = q != 0
            mape = float(np.mean(np.abs(resid[nonzero] / q[nonzero])) * 100) if nonzero.any() else None

            fit_metrics = {"RMSE": rmse, "RMSE_pct": rmse_pct, "MAE": mae, "StdError": std_error, "MAPE": mape}
            metrics_line = (f"- RMSE = {rmse:.2f}" + (f" ({rmse_pct:.1f}% of mean rate)" if rmse_pct is not None else "")
                             + f"\n- MAE = {mae:.2f}\n- Std. Error = {std_error:.2f}"
                             + (f"\n- MAPE = {mape:.1f}%" if mape is not None else "\n- MAPE = n/a (actual values are 0)"))

            for i in range(len(t)):
                export_rows.append({
                    "Column": column,
                    "Model": model_type.title(),
                    "Date": date_strs[i],
                    "Days": int(t[i]),
                    "Actual": float(q[i]),
                    "Fitted": float(q_fit[i]),
                    "Cumulative_Fitted": float(Q_cum[i]),
                })

            dash_style = "solid" if model_type == "hyperbolic" else ("dash" if model_type == "arps" else "dot")
            fig_rate.add_trace(go.Scatter(
                x=df["Date"], y=q_fit, mode="lines", name=f"{column} \u2014 {model_type.title()}",
                line=dict(color=color, dash=dash_style)
            ))

            if show_cum_on_rate:
                fig_rate.add_trace(go.Scatter(
                    x=df["Date"], y=Q_cum, mode="lines", name=f"{column} \u2014 {model_type.title()} Cum",
                    yaxis="y2", line=dict(dash="dot", color=color)
                ))

            fig_cum.add_trace(go.Scatter(
                x=df["Date"], y=Q_cum, mode="lines", name=f"{column} \u2014 {model_type.title()} Cumulative",
                line=dict(color=color)
            ))

            if model_type in ("hyperbolic", "arps"):
                qi, Di, b = params
                col_params[model_type] = {"qi": float(qi), "Di": float(Di), "b": float(b), "Q": float(Q_cum[-1]), **fit_metrics}
                result = f"### {column} \u2014 {model_type.title()}\n- qi = {qi:.2f}\n- Di = {Di:.4f}\n- b = {b:.2f}\n- EUR = {Q_cum[-1]:.2f}\n{metrics_line}"
            elif model_type == "duong":
                qi, a, m = params
                col_params[model_type] = {"qi": float(qi), "a": float(a), "m": float(m), "Q": float(Q_cum[-1]), **fit_metrics}
                result = f"### {column} \u2014 {model_type.title()}\n- qi = {qi:.2f}\n- a = {a:.4f}\n- m = {m:.4f}\n- EUR = {Q_cum[-1]:.2f}\n{metrics_line}"
            else:
                qi, Di = params[:2]
                col_params[model_type] = {"qi": float(qi), "Di": float(Di), "b": None, "Q": float(Q_cum[-1]), **fit_metrics}
                result = f"### {column} \u2014 {model_type.title()}\n- qi = {qi:.2f}\n- Di = {Di:.4f}\n- EUR = {Q_cum[-1]:.2f}\n{metrics_line}"

            col_results.append(dcc.Markdown(result))

        if "total" in model_types and col_params:
            fig_rate.add_trace(go.Scatter(
                x=df["Date"], y=total_curve, mode="lines", name=f"{column} \u2014 Total",
                line=dict(dash="dot", width=3, color=color)
            ))

        results_blocks.extend(col_results)
        params_store[column] = col_params
        actual_data_store[column] = {"t": t.tolist(), "q": q.tolist(), "dates": date_strs}

    if not params_store:
        return go.Figure(), go.Figure(), html.Div("No data"), {}, [], {}, []

    fig_rate.update_layout(
        title="Rate View" + (" \u2014 Comparison" if len(columns) > 1 else ""),
        xaxis=dict(title="Date", rangeslider=dict(visible=True), type="date"),
        yaxis_title="Rate",
        yaxis2=dict(title="Cumulative", overlaying="y", side="right"),
        template="plotly_white"
    )

    fig_cum.update_layout(
        title="Cumulative View" + (" \u2014 Comparison" if len(columns) > 1 else ""),
        xaxis_title="Date",
        yaxis_title="Cumulative",
        template="plotly_white"
    )

    if not show_cum_view:
        fig_cum = go.Figure()

    return fig_rate, fig_cum, results_blocks, params_store, last_t, actual_data_store, export_rows

@app.callback(
    Output("dca-download-csv", "data"),
    Input("export-dca-csv-btn", "n_clicks"),
    State("dca-export-store", "data"),
    prevent_initial_call=True
)
def export_dca_csv(n_clicks, export_rows):
    if not export_rows:
        raise exceptions.PreventUpdate
    df_export = pd.DataFrame(export_rows)
    return dcc.send_data_frame(df_export.to_csv, "dca_export.csv", index=False)

@app.callback(
    Output("dca-download-excel", "data"),
    Input("export-dca-excel-btn", "n_clicks"),
    State("dca-export-store", "data"),
    State("dca-params-store", "data"),
    prevent_initial_call=True
)
def export_dca_excel(n_clicks, export_rows, params_store):
    if not export_rows:
        raise exceptions.PreventUpdate

    df_curves = pd.DataFrame(export_rows)

    summary_rows = []
    for column, models in (params_store or {}).items():
        for model_type, p in models.items():
            summary_rows.append({
                "Column": column,
                "Model": model_type.title(),
                "qi": p.get("qi"),
                "Di": p.get("Di"),
                "b": p.get("b"),
                "a": p.get("a"),
                "m": p.get("m"),
                "EUR": p.get("Q"),
                "RMSE": p.get("RMSE"),
                "RMSE_pct_of_mean": p.get("RMSE_pct"),
                "MAE": p.get("MAE"),
                "StdError": p.get("StdError"),
                "MAPE_pct": p.get("MAPE"),
            })
    df_summary = pd.DataFrame(summary_rows)

    def write_excel(bytes_io):
        with pd.ExcelWriter(bytes_io, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="Summary", index=False)
            df_curves.to_excel(writer, sheet_name="Curve Data", index=False)

    return dcc.send_bytes(write_excel, "dca_export.xlsx")


@app.callback(
    [Output("dca-date-range", "start_date"),
     Output("dca-date-range", "end_date")],
    Input("dca-graph", "relayoutData"),
    prevent_initial_call=True
)
def sync_date_range_from_graph_selection(relayout_data):
    """Dragging the range slider (or zoom-selecting the plot area) under the
    rate chart updates the Date Range picker, which in turn re-fits DCA to
    just that window since it's already an Input to run_dca_model."""
    if not relayout_data:
        raise exceptions.PreventUpdate

    # Plotly sends different key shapes depending on whether the range came from
    # the built-in rangeslider drag or a click-drag zoom on the main plot area.
    if "xaxis.range[0]" in relayout_data and "xaxis.range[1]" in relayout_data:
        start = relayout_data["xaxis.range[0]"]
        end = relayout_data["xaxis.range[1]"]
    elif "xaxis.range" in relayout_data and len(relayout_data["xaxis.range"]) == 2:
        start, end = relayout_data["xaxis.range"]
    else:
        # e.g. double-click autorange reset, or an unrelated layout event
        # (legend click, etc.) - nothing to sync.
        raise exceptions.PreventUpdate

    try:
        start_date = pd.to_datetime(start).strftime("%Y-%m-%d")
        end_date = pd.to_datetime(end).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        raise exceptions.PreventUpdate

    return start_date, end_date

    
@app.callback(
    [Output("debug-params", "children"),
     Output("debug-time", "children")],
    [Input("dca-params-store", "data"),
     Input("dca-time-array", "data")]
)
def debug_outputs(params, time_array):
    return str(params), str(time_array)

@app.callback(
    [Output("mc-fit-selector", "options"),
     Output("mc-fit-selector", "value")],
    Input("dca-params-store", "data")
)
def update_mc_fit_options(params_store):
    if not params_store:
        return [], None
    options = []
    for column, models in params_store.items():
        for model_type in models:
            key = f"{column}::{model_type}"
            label = f"{column} \u2014 {model_type.title()}"
            options.append({"label": label, "value": key})
    default = options[0]["value"] if options else None
    return options, default

@app.callback(
    Output("monte-carlo-graph", "figure"),
    Input("run-monte-carlo-btn", "n_clicks"),
    State("dca-params-store", "data"),
    State("mc-fit-selector", "value"),
    State("dca-actual-data", "data"),
    State("mc-iterations", "value"),
    State("mc-qi-uncertainty", "value"),
    State("mc-di-uncertainty", "value"),
    State("mc-b-uncertainty", "value"),
    State("mc-di-b-correlation", "value"),
    State("mc-q-min", "value"),
    State("mc-show-actual", "value"),
    prevent_initial_call=True
)
def run_monte_carlo(n_clicks, params_store, fit_key, actual_data_store,
                     n_simulations, qi_pct, di_pct, b_pct, di_b_corr, q_min, show_actual):

    if not params_store or not fit_key or "::" not in fit_key:
        raise exceptions.PreventUpdate

    column, model_type = fit_key.split("::", 1)
    if column not in params_store or model_type not in params_store[column]:
        raise exceptions.PreventUpdate

    if model_type == "duong":
        raise exceptions.PreventUpdate  # Duong has (qi, a, m), not (qi, Di, b) - not wired to these controls yet

    params = params_store[column][model_type]
    actual_data = (actual_data_store or {}).get(column)
    if not actual_data or not actual_data.get("t"):
        raise exceptions.PreventUpdate

    t = np.array(actual_data["t"], dtype=float)
    dt = np.diff(t, prepend=t[0])
    dt[dt <= 0] = 1.0

    n_simulations = int(n_simulations or 500)
    qi_pct = float(qi_pct if qi_pct is not None else 5) / 100.0
    di_pct = float(di_pct if di_pct is not None else 10) / 100.0
    b_pct = float(b_pct if b_pct is not None else 15) / 100.0
    rho = float(di_b_corr if di_b_corr is not None else 0.0)
    q_min = float(q_min or 0.0)

    qi_mu = params["qi"]
    Di_mu = params["Di"]
    b_mu = params.get("b")

    rng = np.random.default_rng()

    # abs() because sigma must be non-negative even when a fitted parameter came out
    # negative (e.g. Di<0 for a series that isn't cleanly declining over the fit window)
    qi_sigma = qi_pct * abs(qi_mu)
    di_sigma = di_pct * abs(Di_mu)
    b_sigma = b_pct * abs(b_mu) if b_mu is not None else None

    # qi is sampled independently of Di/b
    qi_samples = rng.normal(qi_mu, qi_sigma, n_simulations)
    qi_samples = np.clip(qi_samples, 1e-6, None)

    if b_mu is not None:
        # Correlate Di and b via a shared standard-normal component so the
        # "Di <-> b correlation" slider actually links the two draws instead
        # of sampling every parameter independently.
        z1 = rng.standard_normal(n_simulations)
        z2 = rng.standard_normal(n_simulations)
        z2_corr = rho * z1 + np.sqrt(max(1 - rho ** 2, 0.0)) * z2

        Di_samples = Di_mu + di_sigma * z1
        b_samples = b_mu + b_sigma * z2_corr

        Di_samples = np.clip(Di_samples, 1e-6, 10.0)
        b_samples = np.clip(b_samples, 0.05, 2.0)
    else:
        Di_samples = rng.normal(Di_mu, di_sigma, n_simulations)
        Di_samples = np.clip(Di_samples, 1e-6, 10.0)
        b_samples = None

    # Vectorized: (n_simulations, 1) params broadcast against (1, n_t) time array
    qi_col = qi_samples[:, None]
    Di_col = Di_samples[:, None]
    t_row = t[None, :]

    if model_type == "exponential":
        sims = qi_col * np.exp(-Di_col * t_row)
    elif model_type == "harmonic":
        sims = qi_col / (1 + Di_col * t_row)
    elif model_type in ("hyperbolic", "arps"):
        b_col = b_samples[:, None]
        sims = qi_col / np.power(1 + b_col * Di_col * t_row, 1 / b_col)
    else:
        raise exceptions.PreventUpdate

    # Economic cutoff applied per-simulation, then EUR = area under the curve up to cutoff
    below_cutoff = sims < q_min
    sims_cut = np.where(below_cutoff, 0.0, sims)
    eur_array = np.sum(sims_cut * dt[None, :], axis=1)

    p10_eur, p50_eur, p90_eur = np.percentile(eur_array, [10, 50, 90])

    # Fan chart: percentile across simulations at each time step (not per-EUR)
    p10_curve = np.percentile(sims, 10, axis=0)
    p50_curve = np.percentile(sims, 50, axis=0)
    p90_curve = np.percentile(sims, 90, axis=0)
    mean_curve = np.mean(sims, axis=0)

    fig = go.Figure()

    # A light sample of individual realizations for visual texture (capped so the
    # figure stays responsive even with thousands of iterations)
    n_shown = min(n_simulations, 40)
    show_idx = np.linspace(0, n_simulations - 1, n_shown).astype(int)
    for i in show_idx:
        fig.add_trace(go.Scatter(
            x=t, y=sims[i, :], mode="lines",
            line=dict(width=1, color="rgba(100,100,100,0.15)"),
            showlegend=False, hoverinfo="skip"
        ))

    # P10-P90 shaded band
    fig.add_trace(go.Scatter(
        x=np.concatenate([t, t[::-1]]),
        y=np.concatenate([p90_curve, p10_curve[::-1]]),
        fill="toself",
        fillcolor="rgba(0,100,255,0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        name="P10-P90 range",
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(x=t, y=p10_curve, mode="lines",
                              line=dict(width=1, dash="dot", color="rgba(0,80,200,0.8)"), name="P10"))
    fig.add_trace(go.Scatter(x=t, y=p90_curve, mode="lines",
                              line=dict(width=1, dash="dot", color="rgba(0,80,200,0.8)"), name="P90"))
    fig.add_trace(go.Scatter(x=t, y=p50_curve, mode="lines",
                              line=dict(width=2, color="rgba(0,60,180,1)"), name="P50 (median)"))
    fig.add_trace(go.Scatter(x=t, y=mean_curve, mode="lines",
                              line=dict(width=3, color="blue"), name="Mean"))

    if show_actual and "show" in show_actual and actual_data:
        fig.add_trace(go.Scatter(
            x=actual_data["t"], y=actual_data["q"], mode="markers",
            marker=dict(size=5, color="black"), name="Actual data"
        ))

    fig.update_layout(
        title=f"Monte Carlo Simulation \u2014 {column} ({model_type.title()}) - {n_simulations} iterations<br>"
              f"P10 EUR={p10_eur:.1f} | P50 EUR={p50_eur:.1f} | P90 EUR={p90_eur:.1f}",
        xaxis_title="Time (days)",
        yaxis_title="Rate",
        template="plotly_white",
        height=500
    )

    return fig

if __name__ == "__main__":
    app.run()