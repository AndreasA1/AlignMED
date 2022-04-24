import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback_context  # pip install dash (version 2.0.0 or higher)
import flask
import numpy as np

from time import sleep
from random import randrange

# testing is false if uploading to rpi
testing = False
n_cells = 30

if not testing:
    import ControlClass
    controller = ControlClass.Controller(n_cells)

server = flask.Flask(__name__)
app = Dash(__name__, server=server)

# # zmq stuff to communicate with controller
# context = zmq.Context()
# socket = context.socket(zmq.PUB)
# socket.bind("tcp://127.0.0.1:6000")


def heat_map(num_rows, num_columns, num_cells):
    if testing:
        df = pd.read_csv("logs/log_test.csv")
    else:
        df = pd.read_csv("logs/log_debug.csv")
    # df = pd.read_csv("logs/log_test.csv")
    df_list = df.values.tolist()[-1][1:]
    df_list = df_list[:num_cells]

    ps_for_hm = []
    for i in range(num_cells):
        ps_for_hm.append(df_list[i])
        if ((i+1) % 10 == 1) or ((i+1) % 10 == 0):
            ps_for_hm.append(df_list[i])
            ps_for_hm.append(df_list[i])
            ps_for_hm.append(df_list[i])
            ps_for_hm.append(df_list[i])
        elif (i+1) % 10 == 5:
            ps_for_hm.append(df_list[i+4])
            ps_for_hm.append(df_list[i-3])

    cells = []
    for i in range(num_cells):
        cells.append(f"Cell {i+1}")
        if ((i+1) % 10 == 1) or ((i+1) % 10 == 0):
            cells.append(f"Cell {i+1}")
            cells.append(f"Cell {i+1}")
            cells.append(f"Cell {i+1}")
            cells.append(f"Cell {i+1}")
        elif (i+1) % 10 == 5:
            cells.append(f"Cell {(i+1)+4}")
            cells.append(f"Cell {(i+1)-3}")

    cells = list(reversed(np.reshape(cells, (num_rows, num_columns)).tolist()))
    pressures = list(reversed(np.reshape(ps_for_hm, (num_rows, num_columns)).tolist()))

    pressures_display = []
    for i in range(len(pressures)):
        n = i // 5
        m = i % 5
        pressures_display.append(round(pressures[n][m], 2))

    fig = go.Figure(data=go.Heatmap(z=pressures,
                                    colorscale=[[0, 'rgb(43,216,43)'], [1, 'rgb(255,0,0)']],
                                    customdata=cells,
                                    hovertemplate="%{customdata}<br>" +
                                                  "Pressure: %{z}<extra></extra>",
                                    zmin=14.7, zmax=15.4
                                    ))
    fig.update_layout(title_text='Pressure Map', width=90*n_columns, height=70*n_rows)
    return fig


def time_series(cell_id=2):
    if testing:
        df = pd.read_csv("logs/log_test.csv")
    else:
        df = pd.read_csv("logs/log_debug.csv")
    # df = pd.read_csv("logs/log_test.csv")

    fig = px.scatter(df, x="Time", y=f"Cell {cell_id}", title=f"Cell {cell_id}", range_y=[14.7, 15.4])
    fig.update_xaxes(title_text='Time (seconds)')
    fig.update_yaxes(title_text='Pressure (PSI)')
    fig.update_traces(mode='lines+markers')
    return fig


# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    html.Div(children=[
        dcc.Graph(id='live-pressure-graph'),

        dcc.Interval(
            id='interval-component',
            interval=3 * 1000,  # in milliseconds
            n_intervals=0),
    ], style={'padding': 10, 'flex': 1}),

    html.Div([
        dcc.Graph(id='pressure-time-series-graph')
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
        html.Button('Initialization: Fill All Cells', id='fill-all-cells', n_clicks=0),
        html.Div(id='container-fill-all-cells-cmd'),
        html.Br(),
        html.Button('Reset Sensor: ', id='btn-reset-sensor', n_clicks=0),
        dcc.Input(id='sensor-id', type='number', placeholder='#'),
        html.Div(id='container-reset-sensor'),
        html.Br(),
        html.Button('Reset Time Series Graph', id='reset-time-series-graph', n_clicks=0),
        html.Div(id='container-reset-time-series-graph'),
        html.Br(),
    ], style={'padding': 10, 'flex': 1})

], style={'display': 'flex', 'flex-direction': 'row'})


# sends command based on entry fields
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
        if (state == 1) or (state == 'Open Inlet'):
            cmd = f"Filling {cell_id} for {duration} seconds"
        else:
            cmd = f"Emptying {cell_id} for {duration} seconds"
        print(cmd)
        if not testing:
            controller.actuate_duration(int(cell_id), int(state), float(duration))
        else:
            print(cell_id, state, duration)
        return html.Div(cmd)

# reset sensor
@app.callback(
    Output('container-reset-sensor', 'children'),
    Input('sensor-id', 'value'),
    Input('btn-reset-sensor', 'n_clicks')
)
def reset_sensor_fun(sensor_id, btn):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'btn-reset-sensor' in changed_id:
        line = f"Resetting sensor {sensor_id}"
        print(line)
        if not testing:
            controller.reset_mpr(sensor_id-1)
        else:
            print("testing new feature")
        return html.Div(line)

# reset time series graph
@app.callback(
    Output('container-reset-time-series-graph', 'children'),
    Input('reset-time-series-graph', 'n_clicks')
)
def reset_time_series_graph(btn):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'reset-time-series-graph' in changed_id:
        line = 'Resetting time series graph'
        print(line)
        if not testing:
            controller.init_log_file()
        else:
            print('testing button')
        return html.Div(line)

# fill all cells
@app.callback(
    Output('container-fill-all-cells-cmd', 'children'),
    Input('fill-all-cells', 'n_clicks')
)
def fill_all_cells(btn):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'fill-all-cells' in changed_id:
        line = 'Filling all cells'
        print(line)

        if not testing:
            controller.fill_all_cells()
        else:
            print('testing')
        return html.Div(line)

# Update live pressure map
@app.callback(Output('live-pressure-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    if not testing:
        print("interval")
        controller.get_sensor_values()
    fig = heat_map(n_rows, n_columns, n_cells)
    return fig


# Update time series line graph
@app.callback(Output('pressure-time-series-graph', 'figure'),
              Input('live-pressure-graph', 'hoverData'),
              Input('interval-component', 'n_intervals'))
def update_time_series(hoverData, n):
    try:
        x = hoverData['points'][0]['x']
        y = 11-hoverData['points'][0]['y']
        box_id = x+y*n_columns
    except TypeError:
        box_id = 1
    cell_ids = [1, 1, 1, 1, 1, 2, 3, 4, 5, 9, 2, 6, 7, 8, 9, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 12, 13, 14, 15, 19, 12, 16, 17, 18, 19, 20, 20, 20, 20, 20, 21, 21, 21, 21, 21, 22, 23, 24, 25, 29, 22, 26, 27, 28, 29, 30, 30, 30, 30, 30]
    fig = time_series(cell_ids[box_id])
    return fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    n_rows = 12
    n_columns = 5

    # if debug is set to True, zmq won't work
    # app.run_server(debug=False, host='127.0.0.1', port=8080)
    app.run_server(debug=True)

    # app.run_server(debug=False, host='0.0.0.0', port=8080)


