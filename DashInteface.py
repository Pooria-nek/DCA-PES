"""

"""
import base64
import datetime
import io
import dash
import dash_bootstrap_components as dbc
from dash import dcc
# import dash_core_components as dcc
# import dash_html_components as html
from dash import html
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
# import dash_table
from dash import dash_table
from os import listdir
from os.path import isfile, join
import numpy as np
from DCA04 import  *
import pickle
import json

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__,
#                 external_stylesheets=external_stylesheets,
#                 )
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#-----------------------------------------------------------------------------
controls1 = dbc.Card(
    [
    #Upload files
    html.H2("Data"),
    html.Hr(),   
    dbc.Row([
        dbc.Row(children=[
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
                "margin": "10px",
            },
            # Allow multiple files to be uploaded
            multiple=True,
            ),
            ],
        ),
        # Checklist
        dbc.Row(children=[
    
            dbc.Row(children=[
                html.H4("Select data columns",         style={"margin-left": "25px","margin-right": "5px"})],
                ),
    
            dbc.Row(children=[
                dcc.Checklist(
                    id="checklistfiles",
                    labelStyle={'display': 'block'},
                    inputStyle={"margin-left": "20px","margin-right": "5px"}
                    
                )
            ])
        ],
            style={'width': '100%', 'padding': '5px 5px', 'display': 'inline-block'},
        ),
        ])

    ],
    body=True,
    color="#F9F9F9",
)
#-----------------------------------------------------------------------------
controls11 = dbc.Card(
    [
    # Preview graph
     html.H4("Preview data"),
     #html.Hr(),     
     html.Div(id='output-data-upload21'),
                dbc.Label("X variable"),
                dcc.Dropdown(
                    id="x-variable",
                    options=[
                        {"label": col, "value": col} for col in pd.DataFrame()
                    ],
                    multi=False                    
                ),


                dbc.Label("Y variable"),
                dcc.Dropdown(
                    id="y-variable",
                    options=[
                        {"label": col, "value": col} for col in pd.DataFrame()
                    ],
                    multi=True                    
                ),

       
        dcc.Checklist(
            id="ChecklistOptionsMonth",
            options=[
                {"label": "Monthly data", "value": "Month"},
            ],
            value=["Month"],
            labelStyle={"display": "inline-block"},
            inputStyle={"margin-left": "20px","margin-right": "5px"}
        ),
    
        dcc.Checklist(
            id="ChecklistOptionsY2",
            options=[
                {"label": "Double Y-Axis", "value": "y2"},
            ],
            value=[],
            labelStyle={"display": "inline-block"},
            inputStyle={"margin-left": "20px","margin-right": "5px"}
        ),  
        html.Div([
        dbc.Row(dcc.Graph(id="cluster-graph")),
        ],  style={"height": "200","width": "80vh"}),
    ],
    body=True,
    color="#F9F9F9",
)
#-----------------------------------------------------------------------------
controls22 = dbc.Card(
    [
    html.Div(id='output-data-upload22'),

    html.H2("Deterministic Analysis"),
    dcc.Checklist(
        id="ChecklistOptionsSum",
        options=[
            {"label": "Show total", "value": "showTotal","disabled":"True"},
        ],
        value=["showTotal"],
        labelStyle={"display": "inline-block"},
        inputStyle={"margin-left": "20px","margin-right": "5px"}
    ),   
    dcc.Checklist(
        id="ChecklistOptionsPeaks",
        options=[
            {"label": "Show peaks", "value": "showPeaks"}
        ],
        value=[],
        labelStyle={"display": "inline-block"},
        inputStyle={"margin-left": "20px","margin-right": "5px"}
    ),  


        dcc.Checklist(
            id="ChecklistOptionsDeclineCurve",
            options=[
                {"label": "Arpes decline curve", "value": "showArpes"},
                {"label": "Duong decline curve", "value": "showDuong"}
            ],
            value=[],
            labelStyle={"display": "inline-block"},
            inputStyle={"margin-left": "20px","margin-right": "5px"}
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
        ],            style={"height": "200","width": "80vh"}),
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
                html.Pre(id='selected-data-printout', style=styles['pre']),md=2),
            dbc.Col(
                html.Pre(id='DCA-parameters-printout', style=styles['pre']),md=2),
            ])
        ], className='three columns'),
    ],
    body=True,
    color="#F9F9F9",
)
controls3 = dbc.Card(
    [
        html.H2("Probabilistic Analysis"),
        html.H5("Economic limit production rate qa:"),
        dbc.Input(type="float", id='inputqa',value=10000),        
        html.Div(id='textarea-Np-output', style={'whiteSpace': 'pre-line'}),
        dbc.Row([
            dbc.Col(dcc.Graph(id="uncertainty-graph"),md=6),
            dbc.Col([
                dbc.Row([
                    dcc.RadioItems(id = 'prob-dist-button',
                                   options = [dict(label = '  Triangular', value = 'Triangular'),
                                              dict(label = '  Normal', value = 'Normal'),
                                              ],
                                   value = 'Triangular',  labelStyle={'display': 'block'})
                    ]),
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.InputGroupText("Tiangular left:"),                        
                            dbc.InputGroupText("%"),                        
                            # dbc.InputGroupAddon(
                            #     id='Triangular-left',
                            #     style={"margin-left":"8px"}),
                            dbc.Input(
                                id="Trinangular-left",
                                placeholder = '%', value=20,min=0, max=100                           
                                )])])
                    ,dbc.Col([
                        dbc.InputGroup([
                            dbc.InputGroupText("Tiangular right:"),                        
                            dbc.InputGroupText("%"),                        
                            dbc.Input(id="Trinangular-right", placeholder = '%',value=20,min=0, max=100)])
                    ])
                    ]),
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.InputGroupText("Normal STD %mean:"),                        
                            dbc.InputGroupText("%"),                        
                            dbc.Input(
                                id="Normal-std",
                                placeholder = '%',value=30, min=0, max=100                           
                                )])])
                    ])
                
                ],md=2)
            ])
    ],
    body=True,
    color="#F9F9F9",

)
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#---------------------LAYOUT---------------------------------------------------
#------------------------------------------------------------------------------
app.layout = html.Div(
    [
    dbc.Container(
        [
            html.H1("PES Tool for Decline Curve Analysis"),
            html.Hr(),
            dcc.Store(id='dataframevalue'),
            dcc.Store(id='dataframepeaksvalue'),
            dcc.Store(id='dataframepeaksvalueUseForDCA'),
            dbc.Row(
                [
                    dbc.Col(controls1, md=6),
                    dbc.Col(controls11, md=6),
                ]),
            
            html.Div(id='div1'),
            dbc.Card(
                [
            
                dbc.Row(
                    [
                        dbc.Col(controls22, md=6),
                        dbc.Col(controls3, md=6),
                    ]),
                ]
            ),
            html.Div(id='div2'),
            dbc.Row(
                [
                    dbc.Col(
                          dash_table.DataTable(id='DataTable',
                                              export_format="csv",
                                              style_data={ 'border': '1px solid black' },
                                              style_header={ 'border': '1px solid black','whiteSpace':'normal' },
                                              style_cell={'fontSize':16, 'font-family':'sans-serif'},
                                              )),
                ]),
            ],
                fluid=True,
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column",     "paper_bgcolor":"#F9F9F9"},
)

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

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
@app.callback([Output(component_id='checklistfiles', component_property='options'),
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
        dff.drop("index", axis=1, inplace=True)
        dffPeaks.drop("index", axis=1, inplace=True)   
        dff=dff.reset_index()
        dffPeaks=dffPeaks.reset_index()
        dffPeaksUseForDCA=pd.concat([dffPeaks[dateCol], dffPeaks['ShowOnGraph']], axis=1)


    checklist_options = [{"label": item.title(), "value": item} for item in dff.columns.to_list()]

    return [checklist_options,dff.to_json(date_format='iso', orient='split'),
            dffPeaks.to_json(date_format='iso', orient='split')]
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
    # sample_list = [contents, filename, ChecklistOptionsMonth]
    # file_name = "GraphSelectedData.pkl"
    # open_file = open(file_name, "wb")
    # pickle.dump(sample_list, open_file)
    # open_file.close()

    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif "txt" or "tsv" in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), delimiter=r"\s+")
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    # drop empty cols    
    df = df.replace({0: np.nan})
    df = df.replace(r'^s*$', np.NaN, regex=True) 
    df = df.dropna(axis='columns', how='all')    
    str=filename+"  : "
    strcols=[str + s for s in df.columns]
    df.columns=strcols    
    # find date column
    df = df.replace({0: np.nan})
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                pass
    dateColdf = df.select_dtypes(include=['datetime64[ns]'])
    dateColIdx = dateColdf.columns[0]
    df= df.rename(columns={dateColIdx: 'Date'})
    dateColIdx='Date'
    if 'Month' in(ChecklistOptionsMonth):       
        # df[xvalue]=df[xvalue].astype('datetime64[ns]')
        df=df.set_index(dateColIdx)
        df=df.resample("MS").mean()    
        df=df.reset_index()
    
    # df=df.set_index(dateColIdx)

    dfPeaks=pd.DataFrame(df[dateColIdx])
    # dfPeaks['ShowOnGraph'] = False    
    for col in df.columns:
        if col!=dateColIdx:
            if df[col].isnull().all()!=True:
            
                df = removeMinima(df, col, 1.2)
                df=fillMissingDates(df,dateColIdx)
                df = removeOutliers(df, col, 3.5)
                df=fillMissingDates(df,dateColIdx)
                indices = findPeaks(df, col, 1.0)
                dfPeaksCol = df[[col]].iloc[indices, :]
                dfPeaks = pd.concat([dfPeaks, dfPeaksCol], axis=1)
                # dfPeaks['ShowOnGraph'].loc[indices] = True
    df=df.reset_index()
    dfPeaks=dfPeaks.reset_index()
        


    return df, dfPeaks, dateColIdx
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