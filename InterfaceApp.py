import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback_context  # pip install dash (version 2.0.0 or higher)
import flask
import zmq
import numpy as np

from time import sleep
from random import randrange

import ControlClass

server = flask.Flask(__name__)
app = Dash(__name__, server=server)

# zmq stuff to communicate with controller
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:6000")

controller = ControlClass.Controller(2)


def heat_map(num_rows, num_columns):
    df = pd.read_csv("logs/log_debug.csv") # log_test has 16 cells
    df_list = df.values.tolist()[-1][1:]
    num_cells = num_columns * num_rows
    df_list = df_list[:num_cells]

    cells = []
    for i in range(num_cells):
        cells.append(f"Cell {i+1}")
    cells = list(reversed(np.reshape(cells, (num_rows, num_columns)).tolist()))
    pressures = list(reversed(np.reshape(df_list, (num_rows, num_columns)).tolist()))

    fig = go.Figure(data=go.Heatmap(z=pressures,
                                    colorscale=[[0, 'rgb(0,255,0)'], [1, 'rgb(255,0,0)']],
                                    customdata=cells,
                                    hovertemplate="%{customdata}<br>" +
                                                  "Pressure: %{z}<extra></extra>",
                                    zmin=14.5
                                    ))
    fig.update_layout(title_text='Pressure Map', width=700, height=700)
    return fig


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
    controller.get_sensor_values()
    fig = heat_map(n_rows, n_columns)
    return fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    n_rows = 1
    n_columns = 2
    n_cells = n_rows*n_columns

    # if debug is set to True, zmq won't work
    app.run_server(debug=False, host='127.0.0.1', port=8080)

    # app.run_server(debug=False, host='0.0.0.0', port=8080)


