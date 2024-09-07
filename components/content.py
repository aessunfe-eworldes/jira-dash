
from dash import dcc, html

# Main content styling
CONTENT_STYLE = {
    "margin-right": "20%",
    "padding": "20px",
    'z-index': '900'
}


content = dcc.Loading(
    id="loading-content",
    type="default",
    children=html.Div(id="page-content", style=CONTENT_STYLE)
)