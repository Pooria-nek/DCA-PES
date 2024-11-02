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
from DCA04 import  *

from used_cards import UPDATE_card, PREVIEW_card

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(children=[
    html.H1(children='Analysis => demo_5'),

    dcc.Store(id='dataframevalue'),

    dbc.Row([
        dbc.Col(UPDATE_card(), width=6),
        dbc.Col(PREVIEW_card(), width=6),
    ]),
])

@app.callback(
    [
        Output('checklistfiles', 'options'),
        Output('dataframevalue', 'data'),
        Output('x-variable', 'options'),
        Output('y-variable', 'options'),
        Output('slice_variable', 'options'),
        Output('cluster-graph', 'figure')
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
        raise PreventUpdate  # Prevent the callback from updating if no file is uploaded

    try:
        # Parse the uploaded data
        dff, dffPeaks, dateCol, non_nan_indices = parse_data(icontents, ifilename, [''])

        # Checklist options for data columns
        checklist_options = [{"label": col, "value": col} for col in dff.columns]
        
        # Options for dropdowns
        dropdown_options = [{'label': col, 'value': col} for col in dff.columns]
        
        # Slice selector based on detected peaks
        slice_selector = [{'label': f'Slice {i}', 'value': i} for i in range(len(dffPeaks))]
        # print(slice_selector)

        if s_var:
            sdf = dff.iloc[s_var]
            print(sdf)
        else :
            sdf = dff
        
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
        # print(figure)
        
        # Return all the options and the figure
        return checklist_options, dff.to_json(date_format='iso', orient='split'), dropdown_options, dropdown_options, slice_selector, figure

    except Exception as e:
        print("Error processing file:", e)
        return [{}], None, [], [], [], {
            'data': [],
            'layout': {'title': 'Error: Could not process file', 'xaxis': {}, 'yaxis': {}}
        }
    

# def update_output(icontents, ifilename, x_var, y_var, graph_type):
#     dff = pd.DataFrame(columns=["Date"])
#     dffPeaks = pd.DataFrame(columns=["Date"])
#     dff = dff.set_index("Date")
#     dffPeaks = dffPeaks.set_index("Date")
#     # tdf = tdf.set_index("test")
#     if icontents:
#         contents = icontents
#         filename = ifilename

#         df1,dfPeaks1,dateCol,non_nan_indices = parse_data(contents, filename,[''])
#         df1 = df1.set_index(dateCol)
#         dfPeaks1 = dfPeaks1.set_index(dateCol)

#         # tdf = pd.concat([splits, tdf], axis=1)
#         dff = pd.concat([dff, df1], axis=1)
#         dffPeaks = pd.concat([dffPeaks, dfPeaks1], axis=1)
        
#         dffPeaks['ShowOnGraph'] = False    
#         dff.drop("index", axis=1, inplace=True)
#         dffPeaks.drop("index", axis=1, inplace=True)   
#         dff=dff.reset_index()
#         dffPeaks=dffPeaks.reset_index()
#         dffPeaksUseForDCA=pd.concat([dffPeaks[dateCol], dffPeaks['ShowOnGraph']], axis=1)

#     print("peakes -> ")
#     print(non_nan_indices)

#     # Split the DataFrame into segments based on the peaks
#     # Split df based on these non-NaN indices
#     splits = []
#     prev_idx = 0
#     for idx in non_nan_indices:
#         split_segment = df1.iloc[prev_idx:idx]  # Get the segment between peaks
#         splits.append(split_segment)
#         prev_idx = idx  # Update the start index for the next split

#     print("split")
#     print(splits)
#     for i, split in enumerate(splits):
#         print(f"\nSplit {i}:\n", split)

#     slice_selector = [{"label": "i", "value": "split"} for i,split in enumerate(splits)]
#     # slice_selector = [{"label": part, "value": part} for part in splits]
#     # print(slice_selector)

#     checklist_options = [{"label": item.title(), "value": item} for item in dff.columns.to_list()]
#     # print(checklist_options)

#     options = [{'label': col, 'value': col} for col in dff.columns]

#     figure = {}
#     if x_var and y_var:
#         figure = {
#             'data': [
#                 {'x': dff[x_var], 'y': dff[y], 'type': graph_type, 'name': y} for y in y_var
#             ],
#             'layout': {
#                 'title': 'Data Preview',
#                 'xaxis': {'title': x_var},
#                 'yaxis': {'title': ', '.join(y_var)}
#             }
#         }
#         #find peak and clean input

#     # print("proccesee -> ")
#     # print(figure)
#     # print("\n\n")
#     # print(options)

#     # slice_selector = [{"label": item, "value": item} for item in dfPeaks1]

#     return [checklist_options,
#             dff.to_json(date_format='iso', orient='split'),
#             options, 
#             options,
#             slice_selector,
#             figure
#             ]


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


# def parse_data(contents, filename, ChecklistOptionsMonth):
#     content_type, content_string = contents.split(",")
#     decoded = base64.b64decode(content_string)
    
#     try:
#         if "csv" in filename:
#             # Assume that the user uploaded a CSV or TXT file
#             df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
#         elif "xls" in filename:
#             # Assume that the user uploaded an excel file
#             df = pd.read_excel(io.BytesIO(decoded))
#         elif "txt" in filename or "tsv" in filename:
#             # Assume that the user uploaded a text/TSV file
#             df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), delimiter=r"\s+")
#     except Exception as e:
#         print(e)
#         return html.Div(["There was an error processing this file."])
    
#     # Drop empty columns
#     df = df.replace({0: np.nan})
#     df = df.replace(r'^s*$', np.NaN, regex=True)
#     df = df.dropna(axis='columns', how='all')

#     # Append filename to each column name
#     str_cols = [filename + " : " + s for s in df.columns]
#     df.columns = str_cols

#     # Find the date column and handle datetime parsing
#     df = df.replace({0: np.nan})
#     for col in df.columns:
#         if df[col].dtype == 'object':
#             try:
#                 df[col] = pd.to_datetime(df[col])
#             except ValueError:
#                 pass

#     dateColdf = df.select_dtypes(include=['datetime64[ns]'])
#     dateColIdx = dateColdf.columns[0]  # Assuming the first datetime column is the date column
#     df = df.rename(columns={dateColIdx: 'Date'})
#     dateColIdx = 'Date'

#     if 'Month' in ChecklistOptionsMonth:
#         # Resample the data monthly
#         df = df.set_index(dateColIdx)
#         df = df.resample("MS").mean()
#         df = df.reset_index()

#     # Find peaks and process data
#     dfPeaks = pd.DataFrame(df[dateColIdx])
    
#     for col in df.columns:
#         if col != dateColIdx and df[col].isnull().all() != True:
#             df = removeMinima(df, col, 1.2)
#             df = fillMissingDates(df, dateColIdx)
#             df = removeOutliers(df, col, 3.5)
#             df = fillMissingDates(df, dateColIdx)
#             indices = findPeaks(df, col, 1.0)
#             dfPeaksCol = df[[col]].iloc[indices, :]
#             dfPeaks = pd.concat([dfPeaks, dfPeaksCol], axis=1)
    
#     df = df.reset_index()
#     dfPeaks = dfPeaks.reset_index()

#     # # Split df based on dfPeaks indices
#     # peak_indices = dfPeaks.index.tolist()  # Get the indices of the peaks
#     # peak_indices.append(len(df))  # Add the end of the DataFrame for the final split
#     # print("peakes -> ")
#     # print(peak_indices)

#     # Now filter out the non-NaN values in dfPeaks
#     non_nan_indices = dfPeaks.dropna(how='any').index.tolist()

#     # Add the final index of the DataFrame to split to the end
#     non_nan_indices.append(len(df))

#     print("peakes -> ")
#     print(non_nan_indices)

#     # Split the DataFrame into segments based on the peaks
#     # Split df based on these non-NaN indices
#     splits = []
#     prev_idx = 0
#     for idx in non_nan_indices:
#         split_segment = df.iloc[prev_idx:idx]  # Get the segment between peaks
#         splits.append(split_segment)
#         prev_idx = idx  # Update the start index for the next split

#     print("\n df -> ")
#     print(df)
#     print("\n dfpeaks -> ")
#     print(dfPeaks)
#     print("\n dfcolindx -> ")
#     print(dateColIdx)
#     print("\n Splits -> ")
#     # for i, split in enumerate(splits):
#     #     print(f"\nSplit {i}:\n", split)

#     return df, dfPeaks, dateColIdx, non_nan_indices

if __name__ == '__main__':
    app.run_server(debug=True)