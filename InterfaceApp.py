import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback_context  # pip install dash (version 2.0.0 or higher)
import flask
import zmq

from time import sleep
from random import randrange

server = flask.Flask(__name__)
app = Dash(__name__, server=server)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:6000")

num_cells = 4
fields = ["Time"]
for i in range(num_cells):
    fields.append(f"Cell {i + 1}")

# df = pd.read_csv("logs/log_debug.csv")
# df = df.groupby(fields)


# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    html.Div(children=[
        dcc.Graph(id='live-pressure-graph'),

        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0),
    ], style={'padding': 10, 'flex': 1}),

    html.Div(children=[
        html.H1("AlignMED", style={'text-align': 'left'}),

        html.Div(id='container-interval-checker'),
        html.Label('Send Commands to Cells:'),
        html.Br(),
        dcc.Input(id='cell-id', type='number', placeholder='Cell #'),
        dcc.RadioItems(id='cell-state',
                    options=[dict(label='Open Inlet', value="1"),
                            dict(label='Open Outlet', value="2")], value='Open Inlet'),
        dcc.Input(id='cell-duration', type='number', placeholder='Command Duration (sec)'),
        html.Br(),
        html.Button('Send Command', id='btn-send-cmd', n_clicks=0),
        html.Div(id='container-last-cmd'),
        html.Br(),
    ], style={'padding': 10, 'flex': 1})

], style={'display': 'flex', 'flex-direction': 'row'})

# # interval checker
# @app.callback(
#     Output('container-interval-checker', 'children'),
#     Input('interval-component', 'n_intervals')
# )
# def display_time(n):
#     df = pd.read_csv("logs/log_test.csv")
#     df = df.groupby(fields)
#     # print(df)
#     zipcode = randrange(1, 100000)
#     temperature = randrange(-80, 135)
#     relhumidity = randrange(10, 60)
#
#     socket.send_string(f"10001 {temperature} {relhumidity}")
#     return html.Div('')


# sends commands based on entry fields
@app.callback(
    Output('container-last-cmd', 'children'),
    Input('cell-id', 'value'),
    Input('cell-state', 'value'),
    Input('cell-duration', 'value'),
    Input('btn-send-cmd', 'n_clicks')
)
def cmd_fun(cell_id, state, duration, btn):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'btn-send-cmd' in changed_id:
        cmd = f"cmd {cell_id} {state} {duration}"
        print(cmd)
        socket.send_string(cmd)
        return html.Div(cmd)


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-pressure-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    # satellite = Orbital('TERRA')
    # data = {
    #     'time': [],
    #     'Latitude': [],
    #     'Longitude': [],
    #     'Altitude': []
    # }

    # # Collect some data
    # for i in range(180):
    #     time = datetime.datetime.now() - datetime.timedelta(seconds=i*20)
    #     lon, lat, alt = satellite.get_lonlatalt(
    #         time
    #     )
    #     data['Longitude'].append(lon)
    #     data['Latitude'].append(lat)
    #     data['Altitude'].append(alt)
    #     data['time'].append(time)

    # Create the graph with subplots
    # fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2)
    # fig['layout']['margin'] = {
    #     'l': 30, 'r': 10, 'b': 30, 't': 10
    # }
    # fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
    #
    # fig.append_trace({
    #     'x': data['time'],
    #     'y': data['Altitude'],
    #     'name': 'Altitude',
    #     'mode': 'lines+markers',
    #     'type': 'scatter'
    # }, 1, 1)
    # fig.append_trace({
    #     'x': data['Longitude'],
    #     'y': data['Latitude'],
    #     'text': data['time'],
    #     'name': 'Longitude vs Latitude',
    #     'mode': 'lines+markers',
    #     'type': 'scatter'
    # }, 2, 1)

    # read updated values from csv file
    df = pd.read_csv("logs/log_test.csv")
    print(df)
    #df = df.groupby(fields)
    print(df)

    fig = px.scatter(df, x="Time", y="Cell 1")
    fig.update_traces(mode='lines+markers')
    #fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0})
    return fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':

    # if debug is set to True, zmq won't work anymore
    app.run_server(debug=False, host='127.0.0.1', port=8080)

    # app.run_server(debug=False, host='0.0.0.0', port=8080)
