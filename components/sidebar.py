
from dash import dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc

# Sidebar styling
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "width": "20%",
    "padding": "20px",
    "background-color": "#f8f9fa",
    "overflow": "auto",
    'z-index': '1000'
}


# Create filter section for each filter specified in config
def create_filter_section(field_name, field_values):
    collapse_id = {'type': 'filter-collapse', 'index': field_name.lower()}
    toggle_id = {'type': 'filter-toggle', 'index': field_name.lower()}
    filter_options_id = {'type': 'filter-options', 'index': field_name.lower()}
    select_all_id = {'type': 'select-all-btn', 'index': field_name.lower()}
    clear_id = {'type': 'clear-btn', 'index': field_name.lower()}
    search_id = {'type': 'search', 'index': field_name.lower()}
    
    return html.Div([
        html.Div([
            html.Label(f'{field_name}', style={'cursor': 'pointer'}, id=toggle_id, className="filter-label"),
        ], style={"margin-bottom": "10px"}),

        dbc.Collapse(
            html.Div([
                html.Label("Search"),
                dcc.Input(id=search_id, type='text', placeholder="Search...", debounce=True),
                html.Div([
                    dbc.Button("Select All", id=select_all_id, n_clicks=0, color='primary', size='sm', style={"margin-right": "10px"}),
                    dbc.Button("Clear", id=clear_id, n_clicks=0, color='secondary', size='sm')
                ], style={"margin-top": "10px"}),
                dcc.Checklist(
                    id=filter_options_id,
                    options=[{'label': i, 'value': i} for i in sorted(field_values)],
                    value=[],  # Empty list means no filters selected (All)
                    labelStyle={'display': 'block'},
                    style={'height': '150px', 'overflowY': 'scroll'}
                )
            ]),
            id=collapse_id,
            is_open=False  # By default, collapse is closed
        ),
    ])


# Main content and sidebar wrapped in loading spinner
sidebar = dcc.Loading(
    id="loading-sidebar",
    type="default",  # Spinner type (default, circle, etc.)
    children=html.Div(id="sidebar", style=SIDEBAR_STYLE)
)
