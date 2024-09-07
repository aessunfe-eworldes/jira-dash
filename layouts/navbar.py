
from dash import dcc, html

navbar = html.Div([
    dcc.Link('Page 1 | ', href='/'),
    dcc.Link('Page 2', href='/page-2'),
])
