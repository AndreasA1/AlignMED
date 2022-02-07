import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback_context  # pip install dash (version 2.0.0 or higher)





app = Dash(__name__)



# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("AlignMED", style={'text-align': 'center'}),
    html.Button('Button 1', id='btn-nclicks-1', n_clicks=0),
    html.Button('Button 2', id='btn-nclicks-2', n_clicks=0),
    html.Br(),
    html.Button('Button 3', id='btn-nclicks-3', n_clicks=0),
    html.Button('Button 4', id='btn-nclicks-4', n_clicks=0),
    html.Div(id='container-button-timestamp')

])

@app.callback(
    Output('container-button-timestamp', 'children'),
    Input('btn-nclicks-1', 'n_clicks'),
    Input('btn-nclicks-2', 'n_clicks'),
    Input('btn-nclicks-3', 'n_clicks'),
    Input('btn-nclicks-4', 'n_clicks')
)
def displayClick(btn1, btn2, btn3, btn4):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'btn-nclicks-1' in changed_id:
        msg = 'Button 1 was most recently clicked'
    elif 'btn-nclicks-2' in changed_id:
        msg = 'Button 2 was most recently clicked'
    elif 'btn-nclicks-3' in changed_id:
        msg = 'Button 3 was most recently clicked'
    elif 'btn-nclicks-4' in changed_id:
        msg = 'Button 4 was most recently clicked'
    else:
        msg = 'None of the buttons have been clicked yet'
    return html.Div(msg)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    #app.run_server(debug=True)

    app.run_server(debug=False, host='0.0.0.0', port=8080)