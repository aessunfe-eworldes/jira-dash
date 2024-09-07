
from dash import dcc, html
from layouts.navbar import navbar

page_1_layout = html.Div([
    navbar,
    html.H1('P1: Tickets Opened and Time in Status'),
    dcc.Graph(id='tickets-opened-graph'),
    dcc.Graph(id='time-in-status-graph')
])
