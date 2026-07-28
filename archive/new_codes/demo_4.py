import dash
import dash_core_components as dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from io import StringIO
import base64
import logging
import numpy as np
import plotly.graph_objs as go
from scipy.signal import find_peaks

import io
from DCA04 import  *

from cards import UPDATE_card, PREVIEW_card, DETERMINISTIC_card, PROBABILISTIC_card

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Set up the layout with a 2x2 grid of cards
app.layout = html.Div(children=[
    html.H1(children='Analysis'),

    dcc.Store(id='dataframevalue'),
    # dcc.Store(id='dataframepeaksvalue'),
    # dcc.Store(id='dataframepeaksvalueUseForDCA'),

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
    [
        Output('checklistfiles', 'options'),
        Output('dataframevalue', 'data'),
        # Output('output-data-preview', 'children'),
        Output('x-variable', 'options'),
        Output('y-variable', 'options'),
        Output('slice_variable', 'options'),
        Output('cluster-graph', 'figure'),
        # Output('dataframepeaksvalue', 'data')
    ],
    [Input(component_id='upload-data', component_property='contents'),
     State(component_id='upload-data', component_property='filename'),
     Input('x-variable', 'value'),
     Input('y-variable', 'value'),
     Input('graph-type', 'value'),
    #  State(component_id='upload-data', component_property='last_modified')
    ],
    prevent_initial_call=True
)
def update_output(icontents, ifilename, x_var, y_var, graph_type):
    dff = pd.DataFrame(columns=["Date"])
    dffPeaks = pd.DataFrame(columns=["Date"])
    dff = dff.set_index("Date")
    dffPeaks = dffPeaks.set_index("Date")
    # tdf = tdf.set_index("test")
    if icontents:
        contents = icontents
        filename = ifilename

        df1,dfPeaks1,dateCol,non_nan_indices = parse_data(contents, filename,[''])
        df1 = df1.set_index(dateCol)
        dfPeaks1 = dfPeaks1.set_index(dateCol)

        # tdf = pd.concat([splits, tdf], axis=1)
        dff = pd.concat([dff, df1], axis=1)
        dffPeaks = pd.concat([dffPeaks, dfPeaks1], axis=1)
        
        dffPeaks['ShowOnGraph'] = False    
        dff.drop("index", axis=1, inplace=True)
        dffPeaks.drop("index", axis=1, inplace=True)   
        dff=dff.reset_index()
        dffPeaks=dffPeaks.reset_index()
        dffPeaksUseForDCA=pd.concat([dffPeaks[dateCol], dffPeaks['ShowOnGraph']], axis=1)
    
    ### for multiple file selection 
    # if icontents:
    #     for i, contents in enumerate(icontents):
    #         contents = icontents[i]
    #         filename = ifilename[i]

    #         df1,dfPeaks1,dateCol = parse_data(contents, filename,[''])
    #         df1 = df1.set_index(dateCol)
    #         dfPeaks1 = dfPeaks1.set_index(dateCol)

    #         dff = pd.concat([dff, df1], axis=1)
    #         dffPeaks = pd.concat([dffPeaks, dfPeaks1], axis=1)
        
    #     dffPeaks['ShowOnGraph'] = False    
    #     dff.drop("index", axis=1, inplace=True)
    #     dffPeaks.drop("index", axis=1, inplace=True)   
    #     dff=dff.reset_index()
    #     dffPeaks=dffPeaks.reset_index()
    #     dffPeaksUseForDCA=pd.concat([dffPeaks[dateCol], dffPeaks['ShowOnGraph']], axis=1)

    # print(dff.columns.to_list())
    # print(dff.count)

    print("peakes -> ")
    print(non_nan_indices)

    # Split the DataFrame into segments based on the peaks
    # Split df based on these non-NaN indices
    splits = []
    prev_idx = 0
    for idx in non_nan_indices:
        split_segment = df1.iloc[prev_idx:idx]  # Get the segment between peaks
        splits.append(split_segment)
        prev_idx = idx  # Update the start index for the next split

    print("split")
    print(splits)
    for i, split in enumerate(splits):
        print(f"\nSplit {i}:\n", split)

    slice_selector = [{"label": "i", "value": "split"} for i,split in enumerate(splits)]
    # slice_selector = [{"label": part, "value": part} for part in splits]
    # print(slice_selector)

    checklist_options = [{"label": item.title(), "value": item} for item in dff.columns.to_list()]
    # print(checklist_options)

    options = [{'label': col, 'value': col} for col in dff.columns]

    figure = {}
    if x_var and y_var:
        figure = {
            'data': [
                {'x': dff[x_var], 'y': dff[y], 'type': graph_type, 'name': y} for y in y_var
            ],
            'layout': {
                'title': 'Data Preview',
                'xaxis': {'title': x_var},
                'yaxis': {'title': ', '.join(y_var)}
            }
        }
        #find peak and clean input

    # print("proccesee -> ")
    # print(figure)
    # print("\n\n")
    # print(options)

    # slice_selector = [{"label": item, "value": item} for item in dfPeaks1]

    return [checklist_options,
            dff.to_json(date_format='iso', orient='split'),
            options, 
            options,
            slice_selector,
            figure
            ]


def parse_data(contents, filename, ChecklistOptionsMonth):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif "txt" in filename or "tsv" in filename:
            # Assume that the user uploaded a text/TSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), delimiter=r"\s+")
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])
    
    # Drop empty columns
    df = df.replace({0: np.nan})
    df = df.replace(r'^s*$', np.NaN, regex=True)
    df = df.dropna(axis='columns', how='all')

    # Append filename to each column name
    str_cols = [filename + " : " + s for s in df.columns]
    df.columns = str_cols

    # Find the date column and handle datetime parsing
    df = df.replace({0: np.nan})
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                pass

    dateColdf = df.select_dtypes(include=['datetime64[ns]'])
    dateColIdx = dateColdf.columns[0]  # Assuming the first datetime column is the date column
    df = df.rename(columns={dateColIdx: 'Date'})
    dateColIdx = 'Date'

    if 'Month' in ChecklistOptionsMonth:
        # Resample the data monthly
        df = df.set_index(dateColIdx)
        df = df.resample("MS").mean()
        df = df.reset_index()

    # Find peaks and process data
    dfPeaks = pd.DataFrame(df[dateColIdx])
    
    for col in df.columns:
        if col != dateColIdx and df[col].isnull().all() != True:
            df = removeMinima(df, col, 1.2)
            df = fillMissingDates(df, dateColIdx)
            df = removeOutliers(df, col, 3.5)
            df = fillMissingDates(df, dateColIdx)
            indices = findPeaks(df, col, 1.0)
            dfPeaksCol = df[[col]].iloc[indices, :]
            dfPeaks = pd.concat([dfPeaks, dfPeaksCol], axis=1)
    
    df = df.reset_index()
    dfPeaks = dfPeaks.reset_index()

    # # Split df based on dfPeaks indices
    # peak_indices = dfPeaks.index.tolist()  # Get the indices of the peaks
    # peak_indices.append(len(df))  # Add the end of the DataFrame for the final split
    # print("peakes -> ")
    # print(peak_indices)


    # Now filter out the non-NaN values in dfPeaks
    non_nan_indices = dfPeaks.dropna(how='any').index.tolist()

    # Add the final index of the DataFrame to split to the end
    non_nan_indices.append(len(df))

    print("peakes -> ")
    print(non_nan_indices)

    # Split the DataFrame into segments based on the peaks
    # Split df based on these non-NaN indices
    splits = []
    prev_idx = 0
    for idx in non_nan_indices:
        split_segment = df.iloc[prev_idx:idx]  # Get the segment between peaks
        splits.append(split_segment)
        prev_idx = idx  # Update the start index for the next split

    print("\n df -> ")
    print(df)
    print("\n dfpeaks -> ")
    print(dfPeaks)
    print("\n dfcolindx -> ")
    print(dateColIdx)
    print("\n Splits -> ")
    # for i, split in enumerate(splits):
    #     print(f"\nSplit {i}:\n", split)


    return df, dfPeaks, dateColIdx, non_nan_indices

# @app.callback(
#     [
#         # Output('DCA-parameters-printout', 'children'),
#         # Output("textarea-Np-output", "children"),
#         # Output("cluster-graph", "figure"),
#         # Output("dca-graph", "figure"),
#         # Output("uncertainty-graph", "figure"),
#         # Output('DataTable', 'data'),
#         # Output('DataTable', 'columns')
#     ],
#     [
#         Input('upload-data', 'contents'),
#         Input('upload-data', 'filename'),
#         # Input("x-variable", "value"),
#         # Input("y-variable", "value"),
#         # Input("ChecklistOptionsPeaks", "value"),
#         Input("ChecklistOptionsMonth", "value"),    
#         # Input("ChecklistOptionsSum", "value"),    
#         # Input("slider_numberofmonths", "value"),    
#         # Input("inputqa", "value"),    
#         Input('dataframevalue', 'data'),
#         Input('dataframepeaksvalue', 'data'),
#         Input('dataframepeaksvalueUseForDCA', 'data'),
#         # Input(component_id='Trinangular-left', component_property='value'),       
#         # Input(component_id='Trinangular-right', component_property='value'),       
#         # Input(component_id='Normal-std', component_property='value'),
#         # Input(component_id='prob-dist-button', component_property='value'),
#         # Input("ChecklistOptionsDeclineCurve", "value")
#     ]
# )
# def make_graph(
#     icontents, ifilename, xvalue, yvalue, ChecklistOptionsPeaks, ChecklistOptionsMonth, ChecklistOptionsSum,
#     numberOfMonths, qa, dfvalue, dfPeaksvalue, dfPeaksvalueForDCA,
#     triangularLeft, triangularRight, normalSTD, DistRadioButton,
#     ChecklistOptionsDeclineCurve
# ):
#     # Initialize variables
#     P05Np, P95Np, meanNp = 0, 0, 0
#     TableData, TableCols = [], []
#     layout = {"xaxis": {"title": "X"}, "yaxis": {"title": "Y"}}

#     # Create figures
#     fig = go.Figure()
#     fig2 = go.Figure()
#     fig3 = go.Figure()
#     fig.update_layout(clickmode='event+select')

#     # Clean yvalue input
#     yvalue = str(yvalue).replace('[', '').replace(']', '').replace("'", '').split(",")

#     # Initialize dataframes
#     df = pd.DataFrame(columns=["Date"])
#     dfPeaks = pd.DataFrame(columns=["Date"])

#     # If file contents are provided, parse them using parse_data
#     if icontents:
#         # Parsing uploaded file
#         df, dfPeaks, dateColIdx = parse_data(icontents, ifilename, ChecklistOptionsMonth)
#         if df is None:
#             return ["Error processing file.", "", go.Figure(), go.Figure(), go.Figure(), [], []]

#         # Select fields based on user input for x and y variables
#         dfSelectedFields = df[[xvalue]]
        
#         # Loop through selected y-values and add traces
#         for yy in yvalue:
#             yy = yy.strip()
#             tempdf = df[[xvalue, yy]].dropna()
            
#             # Add scatter plot for selected y-values
#             fig.add_trace(
#                 go.Scatter(
#                     x=tempdf[xvalue],
#                     y=tempdf[yy],
#                     mode="markers",
#                     marker={"size": 8},
#                     name=yy
#                 )
#             )
        
#         # Handle additional options (e.g., sum, peaks, decline curves)
#         if 'showTotal' in ChecklistOptionsSum:
#             dfSelectedFields['Total'] = dfSelectedFields.sum(axis=1)
            
#             # Add total trace
#             fig2.add_trace(
#                 go.Scatter(
#                     x=df[xvalue],
#                     y=dfSelectedFields['Total'],
#                     mode="markers",
#                     marker={"size": 8, "color": "black", "symbol": "circle"},
#                     name="Total"
#                 )
#             )
        
#         # Further handling for peaks, decline curves, etc. based on the Checklist options

#         # Prepare data for table and return
#         dfTable = dfSelectedFields.reset_index()
#         TableData = dfTable.to_dict('records')
#         TableCols = [{"name": i, "id": i} for i in dfTable.columns]

#     # Prepare final return values
#     strg = "Np= {:.0f}, 90% confidence {:.0f} - {:.0f}".format(float(meanNp), float(P05Np), float(P95Np))
    
#     # Update the layout of the figures
#     fig.update_layout(legend=dict(x=1.5, y=0, traceorder="normal", xanchor="left", yanchor="top"))
#     fig2.update_layout(clickmode='event+select')

#     return strg, strg, fig, fig2, fig3, TableData, TableCols

# @app.callback(
#     Output('uncertainty-graph', 'figure'),
#     [Input('prob-dist-button', 'value'),
#      Input('Triangular-left', 'value'),
#      Input('Triangular-right', 'value'),
#      Input('Normal-std', 'value'),
#      Input('inputqa', 'value')]
# )
# def update_probabilistic_graph(dist_type, tri_left, tri_right, normal_std, qa):
#     figure = {
#         'data': [],
#         'layout': {
#             'title': 'Uncertainty Analysis',
#             'xaxis': {'title': 'Production Rate (qa)'},
#             'yaxis': {'title': 'Probability Density'},
#         }
#     }

#     x_values = np.linspace(0, 2 * qa, 500)

#     if dist_type == "Triangular":
#         mode = qa
#         left = mode - mode * tri_left / 100
#         right = mode + mode * tri_right / 100
#         y_values = np.where((x_values >= left) & (x_values <= right),
#                             (x_values - left) / (mode - left),
#                             (right - x_values) / (right - mode))
#         y_values = np.maximum(y_values, 0)
#         figure['data'].append(go.Scatter(x=x_values, y=y_values, mode='lines', name='Triangular'))

#     elif dist_type == "Normal":
#         mean = qa
#         std_dev = mean * normal_std / 100
#         y_values = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_values - mean) / std_dev) ** 2)
#         figure['data'].append(go.Scatter(x=x_values, y=y_values, mode='lines', name='Normal'))

#     return figure

# @app.callback(
#     [Output('dca-graph', 'figure'),
#      Output('selected-data-printout', 'children'),
#      Output('DCA-parameters-printout', 'children')],
#     [Input('ChecklistOptionsPeaks', 'value'),
#      Input('ChecklistOptionsDeclineCurve', 'value'),
#      Input('slider_numberofmonths', 'value')],
#     [State('upload-data', 'contents'),
#      State('x-variable', 'value'),
#      State('upload-data', 'filename')]
# )
# def update_deterministic_analysis(peaks, decline_curves, num_months, contents, x_var, filename):
#     figure = {
#         'data': [],
#         'layout': {
#             'title': 'Deterministic Analysis',
#             'xaxis': {'title': 'Time'},
#             'yaxis': {'title': 'Value'}
#         }
#     }

#     selected_data = "No data selected"
#     parameters = "No parameters"

#     if contents is not None:
#         if not filename.endswith('.csv'):
#             return figure, selected_data, parameters

#         content_type, content_string = contents.split(',')
#         decoded = base64.b64decode(content_string)
        
#         try:
#             df = pd.read_csv(StringIO(decoded.decode('utf-8')))
#             logging.debug(f"DataFrame created with {len(df)} rows")
#         except Exception as e:
#             logging.error(f"Error parsing CSV: {e}")
#             return figure, selected_data, parameters

#         if 'Production' in df.columns:
#             x_values = df[x_var] if x_var in df.columns else df.index
#             y_values = df['Production']

#             figure['data'].append(go.Scatter(x=x_values, y=y_values, mode='lines', name='Production'))

#             if "showPeaks" in peaks:
#                 # Find peaks
#                 peaks_indices, _ = find_peaks(y_values)
#                 peak_x_values = x_values.iloc[peaks_indices]
#                 peak_y_values = y_values.iloc[peaks_indices]
#                 figure['data'].append(go.Scatter(x=peak_x_values, y=peak_y_values, mode='markers', name='Peaks', marker=dict(color='red', size=8)))

#             if "showArpes" in decline_curves or "showDuong" in decline_curves:
#                 # Add logic for decline curves
#                 pass

#             parameters = f"Number of months: {num_months}"

#     return figure, selected_data, parameters

if __name__ == '__main__':
    app.run_server(debug=True)