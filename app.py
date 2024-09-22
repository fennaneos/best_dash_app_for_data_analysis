import dash
from dash import dcc, html, Input, Output, State, dash_table
from dash import callback_context
import base64
#import dash_html_components as html
#import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
#from dash.dependencies import Input, Output
import json
import io
import requests
import numpy as np

from plotly.subplots import make_subplots

# Load data
df = pd.read_csv('data/stockdata2.csv', index_col=0, parse_dates=True)
df.index = pd.to_datetime(df['Date'])

# Initialize the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True


# The options for the new dropdown
kpi_options = [
    'NbTransactions', 'AvgAAMCorpoRT', 'AvgAAMRT', 'AvgDPRT', 'AvgEngineCPU', 'AvgEngineRT',
    'AvgJSRT', 'AvgTransactionRT', 'AvgAAMEligibilityRT', 'AvgAAMIntegratedRT', 'AvgAVERT', 'AvgSWERT'
]

def get_options(list_stocks):
    dict_list = []
    for i in list_stocks:
        dict_list.append({'label': i, 'value': i})

    return dict_list


app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='four columns div-user-controls',
                             children=[
                                 html.H2('DASH - BFM KPIS ANALYSIS'),
                                 html.P('Visualising time series with Plotly - Dash.'),
                                 html.P('Pick one or more kpis from the dropdown below.'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                            
                                         # Second dropdown for KPI selection
                                         dcc.Dropdown(id='kpi-selector',
                                                       options=[{'label': kpi, 'value': kpi} for kpi in kpi_options],
                                                       multi=True,  # Single selection
                                                       value=kpi_options[0],  # Default value
                                                       style={'backgroundColor': '#1E1E1E'},
                                                       className='kpi-selector'
                                                     ),
                                        

                                         # Flexbox container for date pickers
                                         html.Div([
                                              # Date picker for 'date_from'
                                              html.Div([
                                                  html.P('Date From:'),
                                                  dcc.DatePickerSingle(
                                                      id='date-from',
                                                      date='2024-09-03',
                                                      display_format='YYYY-MM-DD',
                                                      style={'color': 'white'}
                                                  )
                                              ], style={'margin-right': '20px'}),  # Add margin for spacing

                                         # Date picker for 'date_to'
                                         html.Div([
                                                  html.P('Date To:'),
                                                  dcc.DatePickerSingle(
                                                      id='date-to',
                                                      date='2024-09-10',
                                                      display_format='YYYY-MM-DD',
                                                      style={'color': 'white'}
                                                  )
                                              ])
                                          ], style={'display': 'flex', 'alignItems': 'center'})  # Flexbox to align side by side
                                         ,
                                         html.Br(),  # Add spacing

                                         # Input fields for parameters
                                      html.Div([
                                          html.Label('kpiType'),
                                          dcc.Input(id='kpi-type', type='text', value='Evolution',
                                                    style={'width': '100%', 'color': 'white', 'backgroundColor': '#1E1E1E'})
                                      ], style={'margin-bottom': '1px'}),

                                      html.Div([
                                          html.Label('kpiName'),
                                          dcc.Input(id='kpi-name', type='text', value='ResponseTime',
                                                    style={'width': '100%', 'color': 'white', 'backgroundColor': '#1E1E1E'})
                                      ], style={'margin-bottom': '1px'}),

                                      html.Div([
                                          html.Label('viewName'),
                                          dcc.Input(id='view-name', type='text', value='Engine',
                                                    style={'width': '100%', 'color': 'white', 'backgroundColor': '#1E1E1E'})
                                      ], style={'margin-bottom': '1px'}),

                                      html.Div([
                                          html.Label('customerAlias'),
                                          dcc.Input(id='customer-alias', type='text', value='AC0',
                                                    style={'width': '100%', 'color': 'white', 'backgroundColor': '#1E1E1E'})
                                      ], style={'margin-bottom': '1px'}),

                                      html.Div([
                                          html.Label('txn_search_by'),
                                          dcc.Input(id='txn-search-by', type='text', value='message',
                                                    style={'width': '100%', 'color': 'white', 'backgroundColor': '#1E1E1E'})
                                      ], style={'margin-bottom': '1px'}),

                                      html.Div([
                                          html.Label('message'),
                                          dcc.Input(id='message', type='text', value='CALRQT',
                                                    style={'width': '100%', 'color': 'white', 'backgroundColor': '#1E1E1E'})
                                      ], style={'margin-bottom': '10px'}),

                                      html.Div([
                                          html.Label('time_scale'),
                                          dcc.Input(id='time-scale', type='text', value='3600',
                                                    style={'width': '100%', 'color': 'white', 'backgroundColor': '#1E1E1E'})
                                      ], style={'margin-bottom': '1px'}),


                                      # Checkbox for technical_details (default True)
                                      html.Div([
                                          dcc.Checklist(id='technical-details', options=[
                                              {'label': 'Technical Details', 'value': 'True'}],
                                              value=['True'], style={'color': 'white'}
                                          )
                                      ], style={'margin-bottom': '20px'}),
                                         

                                         html.Div([
                                              html.Button("Download Conf", id='download-config-button'),
                                              dcc.Upload(
                                                  id="upload-conf",
                                                  children=html.Button("Upload Conf"),
                                                  multiple=False  # Only single file upload allowed
                                              ),
                                         ], style={'display': 'flex', 'gap': '10px'}),  # Flexbox for horizontal layout and gap for spacing

                                         dcc.Download(id='download-config'),
                                         html.Br(),  # Add spacing


                                      # Flexbox container for side-by-side buttons
                                         html.Div([
                                              html.Button("Download Data", id="btn-download", n_clicks=0),
                                              dcc.Upload(
                                                  id="upload-data",
                                                  children=html.Button("Upload Data"),
                                                  multiple=False  # Only single file upload allowed
                                              ),
                                              # Submit button
                                              html.Button("Submit", id='submit-button', style={'backgroundColor': 'blue', 'color': 'white'})
                                        ], style={'display': 'flex', 'gap': '10px'}),  # Flexbox for horizontal layout and gap for spacing


                                         dcc.Download(id="download-dataframe-csv"),

                                         

                                         html.Div(id="output-data-upload", style={
                                              'height': '300px',  # Scrollable height
                                              'overflowY': 'scroll',  # Enable vertical scroll
                                              'border': '1px solid black',  # Border for visibility
                                              'padding': '10px',
                                              'marginTop': '20px'
                                          }),



                                  # Div to display DataFrame as a table
                                  html.Div([
                                      dash_table.DataTable(
                                          id='data-table',
                                          columns=[],
                                          data=[],
                                          style_table={'overflowX': 'auto'},
                                          style_cell={
                                              'minWidth': '100px', 'width': '100px', 'maxWidth': '200px',
                                              'overflow': 'hidden', 'textOverflow': 'ellipsis'
                                          },
                                      ),

                                      # dcc.Store to hold the DataFrame
                                      dcc.Store(id='stored-data', data={})  # Store to hold the dataframe
                                  ], id='table-container', style={'margin-top': '20px'})
                                     ],

                         

                                  style={'backgroundColor': '#1E1E1E'})
                                ]
                             ),

                    html.Div(className='eight columns div-for-charts bg-grey',
                              children=[
                                  # Graph to display KPI variations over time
                                  dcc.Graph(id='kpi-timeseries',
                                            config={'displayModeBar': False},
                                            animate=True
                                            ),

                                 dcc.Graph(id='kpi-plot',
                                     config={'displayModeBar': False},
                                     animate=True),
                              ])
                             
    ])
        ]

)


# Callback for timeseries price
@app.callback(Output('timeseries', 'figure'),
              [Input('stockselector', 'value')])
def update_timeseries(selected_dropdown_value):
    ''' Draw traces of the feature 'value' based one the currently selected stocks '''
    # STEP 1
    trace = []
    df_sub = df
    # STEP 2
    # Draw and append traces for each stock
    for stock in selected_dropdown_value:
        trace.append(go.Scatter(x=df_sub[df_sub['stock'] == stock].index,
                                 y=df_sub[df_sub['stock'] == stock]['value'],
                                 mode='lines',
                                 opacity=0.7,
                                 name=stock,
                                 textposition='bottom center'))
    # STEP 3
    traces = [trace]
    data = [val for sublist in traces for val in sublist]
    # Define Figure
    # STEP 4
    figure = {'data': data,
              'layout': go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Stock Prices', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
              ),
              }

    return figure

"""
@app.callback(Output('change', 'figure'),
              [Input('stockselector', 'value')])
def update_change(selected_dropdown_value):
    ''' Draw traces of the feature 'change' based one the currently selected stocks '''
    trace = []
    df_sub = df
    # Draw and append traces for each stock
    for stock in selected_dropdown_value:
        trace.append(go.Scatter(x=df_sub[df_sub['stock'] == stock].index,
                                 y=df_sub[df_sub['stock'] == stock]['change'],
                                 mode='lines',
                                 opacity=0.7,
                                 name=stock,
                                 textposition='bottom center'))
    traces = [trace]
    data = [val for sublist in traces for val in sublist]
    # Define Figure
    figure = {'data': data,
              'layout': go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'t': 50},
                  height=250,
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Daily Change', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'showticklabels': False, 'range': [df_sub.index.min(), df_sub.index.max()]},
              ),
              }

    return figure
"""

# Callback to handle data download
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-download", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv(n_clicks):
    # Prepare the CSV data for download
    return dcc.send_data_frame(df.to_csv, "stock_data.csv")


# Helper function to parse the uploaded file
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    
    # Decode the base64 content
    decoded = base64.b64decode(content_string)
    
    try:
        if 'csv' in filename:
            # Assume that the uploaded file is CSV
            df_uploaded = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        else:
            return html.Div(['Only CSV files are supported.'])
        
        # Log the content for debugging
        print(f"DataFrame Loaded from {filename}:")
        print(df_uploaded.head())  # Show the first few rows in the console for debugging
        
        # Create a table displaying the first few rows of the dataframe
        return html.Div([
            dash_table.DataTable(
                data=df_uploaded.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df_uploaded.columns],
                page_size=10,  # Display only a few rows
                style_table={'overflowY': 'scroll'},  # Enable vertical scrolling
                style_cell={
                    'textAlign': 'left',
                    'minWidth': '150px',
                    'width': '150px',
                    'maxWidth': '150px',
                },
                style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'},
                style_data={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'}
            )
        ])
    except Exception as e:
        print(f"Error processing file {filename}: {e}")  # Log the error
        return html.Div(['There was an error processing this file.'])


# Callback to handle file upload and display the DataFrame
"""
@app.callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def update_output(contents, filename):
    if contents is not None:
        return parse_contents(contents, filename)
    return html.Div()
"""

# Callbacks to handle file upload and download configuration
@app.callback(
    Output('download-config', 'data'),
    Input('download-config-button', 'n_clicks'),
    State('date-from', 'date'),
    State('date-to', 'date'),
    State('time-scale', 'value'),
    State('customer-alias', 'value'),
    State('kpi-type', 'value'),
    State('kpi-name', 'value'),
    State('view-name', 'value'),
    State('txn-search-by', 'value'),
    State('message', 'value'),
    State('technical-details', 'value')
)
def download_config(n_clicks, date_from, date_to, time_scale, customer_alias, kpi_type, kpi_name, view_name, txn_search_by, message, technical_details):
    if n_clicks is None:
        return dash.no_update
    
    config = {
        'date_from': date_from,
        'date_to': date_to,
        'time_scale': int(time_scale),
        'customer': customer_alias,
        'display_customer': customer_alias[:2],  # Example logic for display_customer
        'transaction': message,  # Assuming message is used for transaction
        'activation_date': '2024-07-30 09:17:00',  # Fixed value or dynamically set if needed
        'window': 2  # Fixed value or dynamically set if needed
    }
    
    return dict(content=json.dumps(config, indent=4), filename='config.json')




@app.callback(
    [Output('kpi-timeseries', 'figure'),
     Output('output-data-upload', 'children'),
     Output('stored-data', 'data')],
    Input('submit-button', 'n_clicks'),
    Input('upload-data', 'contents'),  # Assuming this is the other button
    State('upload-data', 'filename'),
    State('kpi-selector', 'value'),
    State('date-from', 'date'),
    State('date-to', 'date'),
    State('time-scale', 'value'),
    State('customer-alias', 'value'),
    State('kpi-type', 'value'),
    State('kpi-name', 'value'),
    State('view-name', 'value'),
    State('txn-search-by', 'value'),
    State('message', 'value'),
    State('technical-details', 'value')
)
def handle_submit_and_upload(submit_clicks, contents, filename, selected_kpis, date_from, date_to, time_scale, customer_alias, kpi_type, kpi_name, view_name, txn_search_by, message, technical_details):
    
    #if contents is not None:
    #    return parse_contents(contents, filename)
    #return html.Div()

    # Check which button was clicked
    ctx = callback_context
    print(ctx.triggered)
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # If no button has been clicked yet
    if submit_clicks is None and upload_clicks is None:
        return dash.no_update, dash.no_update, dash.no_update

    # Prepare API parameters
    params = {
        'kpiType': kpi_type,
        'kpiName': kpi_name,
        'viewName': view_name,
        'customerAlias': customer_alias,
        'txn_search_by': txn_search_by,
        'message': message,
        'timeScale': str(time_scale),
        'dateFrom': date_from,
        'dateTo': date_to,
        'technical_details': 'True' in technical_details,
        'graphSelection': set(selected_kpis)
    }

    try:
        api_url = "https://bfmrestapi.tnz.amadeus.net/SSP-RGW/DbQueryRequest/Requests/ESGNMRequest/resultset"
        response = requests.get(api_url, params=params, verify=False)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)

            # Fix the DataFrame to ensure the first row is used as the header
            df.columns = df.iloc[0]  # Set the first row as the column headers
            df = df[1:].reset_index(drop=True)  # Drop the first row and reset the index
            print(df)
            if 'Time' in df.columns:
                df['Time'] = pd.to_datetime(df['Time'])
            else:
                print("No 'Time' column found in the response.")
                return dash.no_update, dash.no_update, dash.no_update

            # Create traces for the graph
            traces = []
            for kpi in selected_kpis:
                if kpi in df.columns:
                    if kpi == 'NbTransactions':
                        # Plot NbTransactions on the secondary y-axis
                        traces.append({ 
                            'x': df['Time'],  # Use the 'Time' column for x-axis
                            'y': df[kpi],
                            'mode': 'lines',
                            'name': kpi,
                            'yaxis': 'y2',  # Assign this trace to the secondary y-axis
                        })
                    else:
                        # Plot other KPIs on the primary y-axis
                        traces.append({ 
                            'x': df['Time'],  # Use the 'Time' column for x-axis
                            'y': df[kpi],
                            'mode': 'lines',
                            'name': kpi,
                            'yaxis': 'y1',  # Assign this trace to the primary y-axis
                        })    

            """
            figure = {
                'data': traces,
                'layout': {
                    'title': f"KPI Variations from {date_from} to {date_to}",
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'KPI Values'},
                    'plot_bgcolor': '#f3f3f3',
                    'paper_bgcolor': '#f3f3f3',
                    'font': {'color': '#1E1E1E'}
                }
            }
            """

            # Define figure with two y-axes
            figure = {
                'data': traces,
                'layout': go.Layout(
                    colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                    template='plotly_dark',
                    paper_bgcolor='rgba(0, 0, 0, 0)',
                    plot_bgcolor='rgba(0, 0, 0, 0)',
                    margin={'b': 15},
                    hovermode='x',
                    autosize=True,
                    title={'text': 'KPIs variations', 'font': {'color': 'white'}, 'x': 0.5},
                    xaxis={'title': 'Time'},
                    yaxis={
                        'title': 'KPIs', 
                        'showgrid': False,
                        'zeroline': False
                    },
                    yaxis2={
                        'title': 'NbTransactions',
                        'overlaying': 'y',
                        'side': 'right',  # Place secondary y-axis on the right side
                        'showgrid': False,
                        'zeroline': False
                    }
                )
            }

            """
            figure = {'data': traces,                                                                                                                                                             
              'layout': go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'KPIs variations', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'title': 'Time'},
              ),
              }
             """


            # Create a styled DataTable with a black background
            table = dash_table.DataTable(
                columns=[{'name': i, 'id': i} for i in df.columns],
                data=df.to_dict('records'),
                style_table={
                    'height': '300px',
                    'overflowY': 'auto',
                    'backgroundColor': '#1E1E1E'
                },
                style_cell={
                    'backgroundColor': '#1E1E1E',
                    'color': 'white',
                    'textAlign': 'left'
                },
                style_header={
                    'backgroundColor': '#1E1E1E',
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                page_size=10
            )

            data = df.to_dict('records')


            # Check which button was pressed and return the appropriate outputs
            if button_id == 'submit-button':
                return figure, table, data
            elif button_id == 'upload-data-button':
                return dash.no_update, table, data
        else:
            print(f"Error: {response.status_code}")
            return dash.no_update, dash.no_update, dash.no_update

    except Exception as e:
        print(f"Exception: {str(e)}")
        return dash.no_update, dash.no_update, dash.no_update



@app.callback(
    Output('kpi-plot', 'figure'),  # The graph element to replace "Daily changes"
    Input('submit-button', 'n_clicks'),  # Use the submit button as the trigger
    State('kpi-selector', 'value'),
    State('date-from', 'date'),
    State('date-to', 'date'),
    State('time-scale', 'value'),
    State('customer-alias', 'value'),
    State('kpi-type', 'value'),
    State('kpi-name', 'value'),
    State('view-name', 'value'),
    State('txn-search-by', 'value'),
    State('message', 'value'),
    State('technical-details', 'value'),
    State('stored-data', 'data')  # Include DataTable's data as input
)
def update_kpi_plot(n_clicks, selected_kpis, date_from, date_to, time_scale, customer_alias, kpi_type, kpi_name, view_name, txn_search_by, message, technical_details, table_data):
    if n_clicks is None:
        return dash.no_update

    try:
        # If the data table is not empty, convert it back to a pandas DataFrame
        if table_data:
            df = pd.DataFrame(table_data)
        else:
            print("No data available in the DataTable")
            return dash.no_update

        # Convert 'Time' column to datetime
        if 'Time' in df.columns:
            df['Time'] = pd.to_datetime(df['Time'])
        else:
            print("No 'Time' column found in the DataFrame.")
            return dash.no_update

        print("df: ", df)
        # Calculate KPIs using the existing functions
        print("computing moving averages")
        moving_averages = calculate_moving_averages(df)
        print("moving volume weighted averages")
        moving_volume_weighted_averages = calculate_moving_volume_weighted_average(df)
        print("cumulative weighted kpis")
        cumulative_weighted_kpis = calculate_cumulative_volume_weighted_kpis(df)

        # Plot the KPIs using the provided function
        print("Plotting Data")
        kpi_figure = plot_kpis(df, cumulative_weighted_kpis, moving_averages, moving_volume_weighted_averages)

        return kpi_figure

    except Exception as e:
        print(f"Error in plotting KPIs: {str(e)}")
        return dash.no_update


def calculate_cumulative_volume_weighted_kpis(df):
    cumulative_weighted_kpis = pd.DataFrame(index=df.index)

    kpi_columns = df.columns
    for kpi in kpi_columns:
        cum_weighted_sum = 0
        cum_transaction_sum = 0

        # Ensure data is in numeric format and handle missing or inf values
        df[kpi] = pd.to_numeric(df[kpi], errors='coerce').fillna(0)
        df["NbTransactions"] = pd.to_numeric(df["NbTransactions"], errors='coerce').fillna(0)

        for i in range(len(df)):
            # Ensure you handle any invalid or large data appropriately
            try:
                kpi_value = df[kpi].iloc[i]
                nb_transactions = df["NbTransactions"].iloc[i]

                # Avoid overflow by casting to float or using np.clip to limit values
                kpi_value = np.float64(kpi_value)
                nb_transactions = np.float64(nb_transactions)

                # Perform cumulative sum with safeguards
                cum_weighted_sum += kpi_value * nb_transactions
                cum_transaction_sum += nb_transactions

                if cum_transaction_sum != 0:
                    cumulative_weighted_kpis.at[i, kpi] = cum_weighted_sum / cum_transaction_sum
                else:
                    cumulative_weighted_kpis.at[i, kpi] = 0  # Avoid division by zero

            except Exception as e:
                print(f"Error calculating cumulative weighted KPI for {kpi} at index {i}: {e}")
                cumulative_weighted_kpis.at[i, kpi] = 0  # Handle the error gracefully

    return cumulative_weighted_kpis



def calculate_moving_averages(df):
    print("df.index: ", df.index)
    moving_averages = pd.DataFrame(index=df.index)
    window_size = 2
    #window_size = self._window * int(SECONDS_PER_DAY / self._scale)  # scale is in seconds
    #for kpi in self._kpi_columns:
    for kpi in df.columns:
        print("kpi: ", kpi)
        print(df)
        df[kpi] = pd.to_numeric(df[kpi], errors='coerce')
        moving_averages[kpi] = df[kpi].rolling(window=window_size).mean()
    return moving_averages

def calculate_moving_volume_weighted_average(df):
    volume_weighted_averages = pd.DataFrame(index=df.index)
    window_size = 2
    #window_size = self._window * int(SECONDS_PER_DAY / self._scale)  # scale is in seconds
    #for kpi in self._kpi_columns:
    for kpi in df.columns:
        print("kpi: ", kpi)
        def weighted_sum(x):
            index = x.index
            return (x * df.loc[index, "NbTransactions"]).sum()

        # Calculate cumulative weighted KPIs
        cumulative_weighted_kpis = df[kpi].rolling(window=window_size).apply(weighted_sum)
        cumulative_weights = df["NbTransactions"].rolling(window=window_size).sum()

        # Calculate volume weighted average
        volume_weighted_averages[kpi] = cumulative_weighted_kpis / cumulative_weights
    return volume_weighted_averages


def plot_kpis(df, cumulative_weighted_kpis, moving_averages, moving_volume_weighted_averages):
    # Create a subplot grid with each KPI in a separate row
    num_kpis = len(df.columns)
    
    fig = make_subplots(rows=num_kpis, cols=1, shared_xaxes=True, subplot_titles=df.columns)

    # Use the "Time" column as the x-axis
    time_values = df['Time']

    # Loop through KPI columns to plot each one
    kpi_columns = [col for col in df.columns if col != 'Time']
    for i, kpi in enumerate(kpi_columns, start=1):
        # Plot the raw KPI data
        fig.add_trace(go.Scatter(
            x=time_values,  # Use the 'Time' column for x-axis
            y=df[kpi],
            mode='lines',
            name=f"{kpi}",
            line=dict(color='blue'),
        ), row=i, col=1)
        
        # Plot cumulative volume-weighted KPIs
        fig.add_trace(go.Scatter(
            x=time_values,  # Use the 'Time' column for x-axis
            y=cumulative_weighted_kpis[kpi],
            mode='lines',
            name=f"{kpi} (cumulative volume-weighted)",
            line=dict(color='orange', dash='dash'),
        ), row=i, col=1)

        # Plot moving averages
        fig.add_trace(go.Scatter(
            x=time_values,  # Use the 'Time' column for x-axis
            y=moving_averages[kpi],
            mode='lines',
            name=f"{kpi} (moving average)",
            line=dict(color='red', dash='dot'),
        ), row=i, col=1)

        # Plot moving volume-weighted averages
        fig.add_trace(go.Scatter(
            x=time_values,  # Use the 'Time' column for x-axis
            y=moving_volume_weighted_averages[kpi],
            mode='lines',
            name=f"{kpi} (moving volume-weighted average)",
            line=dict(color='black', dash='dashdot'),
        ), row=i, col=1)

    # Update the layout of the figure
    fig.update_layout(
        height=300 * num_kpis,  # Adjust the height based on the number of KPIs
        showlegend=True,
        template='plotly_dark',  # Keep dark theme
        title="KPIs with Cumulative Volume-Weighted and Moving Averages",
        xaxis_title="Time",
        yaxis_title="KPI Value"
    )

    # Return the Plotly figure to be used in Dash
    return fig


"""
def plot_kpis(df, cumulative_weighted_kpis, moving_averages, moving_volume_weighted_averages):
    fig = go.Figure()
    print("here")
    print("moving_averages: ", moving_averages)
    print("cumulative_weighted_kpis: ", cumulative_weighted_kpis)
    print("moving_volume_weighted_averages: ", moving_volume_weighted_averages)
    # Loop through KPI columns to plot each one
    for kpi in df.columns:
        # Plot the raw KPI data
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[kpi],
            mode='lines',
            name=f"{kpi}",
            line=dict(color='blue'),
        ))

        # Plot cumulative volume-weighted KPIs
        fig.add_trace(go.Scatter(
            x=cumulative_weighted_kpis.index,
            y=cumulative_weighted_kpis[kpi],
            mode='lines',
            name=f"{kpi} (cumulative volume-weighted)",
            line=dict(color='orange', dash='dash'),
        ))

        # Plot moving averages
        fig.add_trace(go.Scatter(
            x=moving_averages.index,
            y=moving_averages[kpi],
            mode='lines',
            #name=f"{kpi} {self._window}-day MA",
            line=dict(color='red', dash='dot'),
        ))

        # Plot moving volume-weighted averages
        fig.add_trace(go.Scatter(
            x=moving_volume_weighted_averages.index,
            y=moving_volume_weighted_averages[kpi],
            mode='lines',
            #name=f"{kpi} {window}-day MVWA",
            line=dict(color='black', dash='dashdot'),
        ))

    # Add vertical line for the activation date
    #fig.add_vline(
    #    x=pd.to_datetime(self._activation_date),
    #    line=dict(color='purple', dash='dot'),
    #    annotation_text="Activation Date",
    #    annotation_position="top right"
    #)

    # Add titles and labels
    fig.update_layout(
        #title=f"KPIs with Cumulative Volume-Weighted and Moving Averages {self._display} / {self._txn_name}",
        xaxis_title="Time",
        yaxis_title="KPI Value",
        legend_title="KPIs",
        template='plotly_dark',  # Optional: Keep the dark theme for consistency with your layout
    )

    # Return the Plotly figure to be used in Dash
    return fig
"""

if __name__ == '__main__':
    app.run_server(debug=True)
