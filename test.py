
import dash
from dash import html
from dash import dcc
from collections import deque
import math
from dash.dependencies import Input, Output, State
from dash import ctx
import dash_bootstrap_components as dbc
import math as m


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  # remove "Updating..." from title


X = []
Y = []
length_data = []
length_data.append(0)

app.layout=dbc.Container([
    dbc.Row([
        dbc.Col([
            # format and display current x value
            html.Div("X(um)", style={'margin-top':'5%', 'font-size' : '18px',
                                     'margin-left' : '2%'}),
            html.Div("current x", id='current_x', style={'margin-left': '23%', 'border': '1px solid gray',
                                            'width' : '350px', 'height' : '26px',
                                            'background-color': 'floralwhite', 'margin-top': '-5%'}),

            # format and display current y value
            html.Div("Y(um)", style={'font-size' : '18px', 'margin-left' : '2%'}),
            html.Div(id='current_y', style={'margin-left': '23%', 'border': '1px solid gray',
                                            'width': '350px', 'height': '26px',
                                            'background-color': 'floralwhite', 'margin-top': '-5%'}),

            # format and display current y value
            html.Div("Z(um)", style={'font-size' : '18px', 'margin-left' : '2%'}),
            html.Div("z value displayed here", style={'margin-left': '23%', 'border': '1px solid gray',
                                                      'width': '350px', 'height': '26px',
                                                      'background-color': 'floralwhite', 'margin-top': '-5%'}),

            # format user input for x,y,z value
            html.Div("Xt(um)", style={'font-size': '18px', 'margin-left': '2%', 'border-top' : '2px dashed thistle',
                                      'margin-top' : '5%'}),
            dcc.Input("0", id="set_x", type="number", style={'margin-left': '23%', }, step=0.2),

            html.Div("Yt(um)", style={'font-size': '18px', 'margin-left': '2%', }),
            dcc.Input("0", id="set_y", type="number", style={'margin-left': '23%', }, step=0.2),

            html.Div("Zt(um)", style={'font-size': '18px', 'margin-left': '2%', }),
            dcc.Input(id="set_z", type="number", style={'margin-left': '23%', }, step=0.2),

            # create go-to button
            html.Br(),
            html.Button('Go to', id='go_to', style={'margin-left' : '8%',  'width' : '300px', 'margin-top' : '2%',
                                                    'border' : '2px inset', 'background-color' : 'lavender',
                                                    'border-radius': '6px', 'height': '40px'}),

            # create and format x,y span inputs
            html.Div("Xspan(um)", style={'font-size': '18px', 'margin-left': '2%', 'border-top' : '2px dashed thistle',
                                         'margin-top' : '4%'}),
            dcc.Input("10", id="x_span", type="number", style={'margin-left': '23%',}, step=0.2, debounce=True),

            html.Div("Yspan(um)", style={'font-size': '18px', 'margin-left': '2%', }),
            dcc.Input("10", id="y_span", type="number", style={'margin-left': '23%',}, step=0.2, debounce=True),

            # create and format V, dx, dy inputs
            html.Div("V(nm/sec)", style={'font-size': '18px', 'margin-left': '2%', 'margin-top' : '2%'}),
            dcc.Input("2000", id="velocity", type="number", style={'margin-left': '23%',}, step=0.2),

            html.Div("dx(nm)", style={'font-size': '18px', 'margin-left': '2%', 'margin-top' : '2%'}),
            dcc.Input("1",id="dx", type="number", style={'margin-left': '23%',}, step=0.1),

            html.Div("dy(nm)", style={'font-size': '18px', 'margin-left': '2%', 'margin-top' : '2%'}),
            dcc.Input("1", id="dy", type="number", style={'margin-left': '23%',}, step=0.1),

            # create scan button
            html.Br(),
            html.Button('Scan', id='scan', style={'margin-left' : '8%',  'width' : '300px', 'margin-top' : '2%',
                                                    'border' : '2px inset', 'background-color' : 'lavender',
                                                    'border-radius': '6px', 'height': '40px'}),
            html.Button('Stop/Resume', id='stop', style={'margin-left' : '8%',  'width' : '300px', 'margin-top' : '2%',
                                                    'border' : '2px inset', 'background-color' : 'pink',
                                                    'border-radius': '6px', 'height': '40px'}),

        ],  align='start', width=4),

        dbc.Col([
            dcc.Graph(id='graph',  style={'height': '100vh', 'width' : '100vh', 'margin-left' : '10%'},  clickData=None,
                      hoverData=None),
            dcc.Interval(id="interval_hardware", interval=500, disabled=True),
            dcc.Interval(id="interval_gui", disabled=True),
            html.Div(id='hidden-div', style={'display': 'none'}),
            html.Div(id='nothing', style={'display': 'none'})


        ], width=8)
    ], justify='start')
], fluid=True, style={'background-color': 'ghostwhite'})



# setting x, y
@app.callback(Output('current_x', 'children'),
              Output('current_y', 'children'),
              [State('set_x', 'value'),
               State('set_y', 'value'),
               Input('go_to', 'n_clicks')])
def setting_x(valuex, valuey, n_clicks):
    return valuex, valuey

@app.callback(
    Output("set_x", "value"),
    Output("set_y", "value"),
    Input("graph", "clickData"),
)
def click(clickData):
    if not clickData:
        raise dash.exceptions.PreventUpdate
    return float(clickData["points"][0]['x']),float(clickData["points"][0]['y'])

@app.callback(Output('graph', 'figure'),
               [Input('scan', 'n_clicks'),
                Input('go_to', 'n_clicks'),
               State('x_span', 'value'),
               State('y_span', 'value'),
               State('set_x', 'value'),
               State('set_y', 'value'),
               ])
def update_axis(click1, click2, spanx, spany, setx, sety):

    trace1 = {'x': [], 'y' : []}
    trace2 = {'x': [int(setx)], 'y': [int(sety)]}
    if "go_to" == ctx.triggered_id:
        trace2 = {'x' : [int(setx)], 'y' : [int(sety)]}
        return dict(data=[trace1, trace2],
                    layout=dict(xaxis=dict(range=[int(spanx) * (-1), int(spanx)]),
                                yaxis=dict(range=[int(spany) * (-1),  int(spany)])))
    else:

        return dict(data=[trace1, trace2],
              layout=dict(xaxis=dict(range=[int(setx) - int(spanx) /2 - 1, int(setx) + int(spanx)/2 + 1]),
                          yaxis=dict(range=[int(sety) - int(spany) /2 - 1, int(sety) + int(spany)/2 + 1])))

@app.callback(Output('graph', 'extendData'),
              [ State('interval_hardware', 'disabled'),
                Input('interval_gui', 'n_intervals'),
              ])
def extend_data(state, n):
    length_data.append(len(X))
    #print(length_data)
    #print(X)
    print(state)
    return dict(x=[ X[0:]], y=[ Y[0:] ]) , [0], 1000


@app.callback(Output('nothing', 'children'),
              [Input('interval_hardware', 'n_intervals'),
               State('x_span', 'value'),
               State('y_span', 'value'),
               State('set_x', 'value'),
               State('set_y', 'value'),
               State('dx', 'value'),
               State('dy', 'value'),
               ])
def update_hardware(n, spanx, spany, setx, sety, dx, dy):
    if (float(dx) < 1):
        num_points_row =  int(int(spanx) // float(dx)) + 2
    else:
        num_points_row = int(spanx) // float(dx) + 1

    y = int(sety) + int(spany) / 2 - float(dy) * (int(n) // num_points_row)

    if (n==0):
        x = int(setx) + int(spanx) * (-1) / 2

    #even row (x traverse right)
    elif ((int(n) // num_points_row) % 2 == 0):
        x = int(setx) + int(spanx) * (-1) / 2 + (int(n) % num_points_row) * float(dx)

    #odd row
    else:
        x = int(setx) + int(spanx) / 2 - ((int(n)) % num_points_row) * float(dx)

    X.append(x)
    Y.append(y)
    return 0

@app.callback(Output('interval_gui', 'n_intervals'),
              Output('interval_gui', 'interval'),
              Output('interval_gui', 'disabled'),
              [State('velocity', 'value'),
               State('interval_gui', 'n_intervals'),
               State('interval_gui', 'disabled'),
              Input('scan', 'n_clicks'),
               Input('go_to', 'n_clicks'),
               Input('stop', 'n_clicks')])
def restart_interval(vel, interval, disabled, scan, go_to, stop):
    if 'scan' == ctx.triggered_id:
        return 0, (1 / int(vel)) * pow(10,6), False
    elif 'stop' == ctx.triggered_id:
        if (disabled == True):
            return interval, (1 / int(vel)) * pow(10,6), False
        else:
            return interval, 0, True
    else:
        return 0, 0, True

@app.callback(Output('interval_hardware', 'n_intervals'),
              Output('interval_hardware', 'interval'),
              Output('interval_hardware', 'disabled'),
              [State('velocity', 'value'),
               State('interval_hardware', 'n_intervals'),
               State('interval_hardware', 'disabled'),
              Input('scan', 'n_clicks'),
               Input('go_to', 'n_clicks'),
               Input('stop', 'n_clicks')])
def restart_interval(vel, interval, disabled, scan, go_to, stop):
    if 'scan' == ctx.triggered_id:
        return 0, 500, False
    elif 'stop' == ctx.triggered_id:
        if (disabled == True):
            return interval, 500, False
        else:
            return interval, 0, True
    else:
        return 0, 0, True

if __name__ == '__main__':
        app.run_server(debug=True)