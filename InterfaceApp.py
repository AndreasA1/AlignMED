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

    html.H1("AlignMED", style={'text-align': 'left'}),
    html.Button('Fill Cell 1', id='btn-nclicks-1', n_clicks=0),
    html.Button('Empty Cell 1', id='btn-nclicks-2', n_clicks=0),
    html.Br(),
    html.Button('Fill Cell 2', id='btn-nclicks-3', n_clicks=0),
    html.Button('Empty Cell 2', id='btn-nclicks-4', n_clicks=0),
    html.Br(),
    html.Button('Fill Cell 3', id='btn-nclicks-5', n_clicks=0),
    html.Button('Empty Cell 3', id='btn-nclicks-6', n_clicks=0),
    html.Br(),
    html.Button('Fill Cell 4', id='btn-nclicks-7', n_clicks=0),
    html.Button('Empty Cell 4', id='btn-nclicks-8', n_clicks=0),
    html.Br(),
    html.Div(id='container-button-timestamp'),
    html.Div(id='container-interval-checker'),
    dcc.Interval(
        id='interval-component',
        interval=1 * 1000,  # in milliseconds
        n_intervals=0
    )
])


# button press checker
@app.callback(
    Output('container-button-timestamp', 'children'),
    Input('btn-nclicks-1', 'n_clicks'),
    Input('btn-nclicks-2', 'n_clicks'),
    Input('btn-nclicks-3', 'n_clicks'),
    Input('btn-nclicks-4', 'n_clicks'),
    Input('btn-nclicks-5', 'n_clicks'),
    Input('btn-nclicks-6', 'n_clicks'),
    Input('btn-nclicks-7', 'n_clicks'),
    Input('btn-nclicks-8', 'n_clicks')
)
def display_click(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'btn-nclicks-1' in changed_id:
        msg = 'Filling Cell 1'
    elif 'btn-nclicks-2' in changed_id:
        msg = 'Emptying Cell 1'
    elif 'btn-nclicks-3' in changed_id:
        msg = 'Filling Cell 2'
    elif 'btn-nclicks-4' in changed_id:
        msg = 'Emptying Cell 2'
    elif 'btn-nclicks-5' in changed_id:
        msg = 'Filling Cell 3'
    elif 'btn-nclicks-6' in changed_id:
        msg = 'Emptying Cell 3'
    elif 'btn-nclicks-7' in changed_id:
        msg = 'Filling Cell 4'
    elif 'btn-nclicks-8' in changed_id:
        msg = 'Emptying Cell 4'
    else:
        msg = 'None of the buttons have been clicked yet'
    return html.Div(msg)


# interval checker
@app.callback(Output('container-interval-checker', 'children'),
              Input('interval-component', 'n_intervals')
)
def display_time(n):
    df = pd.read_csv("logs/log_test.csv")
    df = df.groupby(fields)
    # print(df)
    zipcode = randrange(1, 100000)
    temperature = randrange(-80, 135)
    relhumidity = randrange(10, 60)

    socket.send_string(f"10001 {temperature} {relhumidity}")
    return html.Div('')


# ------------------------------------------------------------------------------
if __name__ == '__main__':

    # if debug is set to True, zmq won't work anymore
    app.run_server(debug=False, host='127.0.0.1', port=8080)

    # app.run_server(debug=False, host='0.0.0.0', port=8080)
