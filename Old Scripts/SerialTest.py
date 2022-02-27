#tests raw data coming in from esp

import serial
import time

ser = serial.Serial()
ser.baudrate = 115200
ser.port = 'COM7'
ser.open()

while not ser.is_open:
    print('not connected')
    time.sleep(1)


while True:
    #localtime = time.localtime()
    line = ser.readline()
    print(line)


#throwing some old shit in here just in case
    # html.Button('Fill Cell 1', id='btn-nclicks-1', n_clicks=0),
    # html.Button('Empty Cell 1', id='btn-nclicks-2', n_clicks=0),
    # html.Br(),
    # html.Button('Fill Cell 2', id='btn-nclicks-3', n_clicks=0),
    # html.Button('Empty Cell 2', id='btn-nclicks-4', n_clicks=0),
    # html.Br(),
    # html.Button('Fill Cell 3', id='btn-nclicks-5', n_clicks=0),
    # html.Button('Empty Cell 3', id='btn-nclicks-6', n_clicks=0),
    # html.Br(),
    # html.Button('Fill Cell 4', id='btn-nclicks-7', n_clicks=0),
    # html.Button('Empty Cell 4', id='btn-nclicks-8', n_clicks=0),
    # html.Br(),
    # html.Div(id='container-button-timestamp'),
# button press checker
# @app.callback(
#     Output('container-button-timestamp', 'children'),
#     Input('btn-nclicks-1', 'n_clicks'),
#     Input('btn-nclicks-2', 'n_clicks'),
#     Input('btn-nclicks-3', 'n_clicks'),
#     Input('btn-nclicks-4', 'n_clicks'),
#     Input('btn-nclicks-5', 'n_clicks'),
#     Input('btn-nclicks-6', 'n_clicks'),
#     Input('btn-nclicks-7', 'n_clicks'),
#     Input('btn-nclicks-8', 'n_clicks')
# )
# def display_click(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8):
#     changed_id = [p['prop_id'] for p in callback_context.triggered][0]
#     if 'btn-nclicks-1' in changed_id:
#         msg = 'Filling Cell 1'
#     elif 'btn-nclicks-2' in changed_id:
#         msg = 'Emptying Cell 1'
#     elif 'btn-nclicks-3' in changed_id:
#         msg = 'Filling Cell 2'
#     elif 'btn-nclicks-4' in changed_id:
#         msg = 'Emptying Cell 2'
#     elif 'btn-nclicks-5' in changed_id:
#         msg = 'Filling Cell 3'
#     elif 'btn-nclicks-6' in changed_id:
#         msg = 'Emptying Cell 3'
#     elif 'btn-nclicks-7' in changed_id:
#         msg = 'Filling Cell 4'
#     elif 'btn-nclicks-8' in changed_id:
#         msg = 'Emptying Cell 4'
#     else:
#         msg = 'None of the buttons have been clicked yet'
#     return html.Div(msg)
