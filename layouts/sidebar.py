import json
from dash import dcc, html
import dash_bootstrap_components as dbc

from services.config_service import load_filter_config


# Sidebar styling
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "width": "20%",
    "padding": "20px",
    "background-color": "#f8f9fa",
    "overflow": "auto",  # Allow scrolling
}


def create_categorical_filter_section(field_name, field_values):
    """Create a Power BI-style filter section for categorical data."""
    collapse_id = f'{field_name.lower()}-collapse'
    return html.Div([
        # The clickable label that will toggle the collapse
        html.Div([
            html.Label(f'{field_name}', style={'cursor': 'pointer'}, id=f'{field_name.lower()}-toggle', className="filter-label"),
        ], style={"margin-bottom": "10px"}),

        # The collapsible section that contains the dropdown and filter options
        dbc.Collapse(
            html.Div([
                dcc.Dropdown(
                    id=f'{field_name.lower()}-filter-type',
                    options=[{'label': 'Basic filtering', 'value': 'basic'}, {'label': 'Advanced filtering', 'value': 'advanced'}],
                    value='basic',
                    clearable=False,
                    style={'width': '95%'}
                ),
                html.Div([
                    html.Label("Search"),
                    dcc.Input(id=f'{field_name.lower()}-search', type='text', placeholder="Search...", debounce=True),
                    html.Div([
                        dbc.Button("Select All", id=f'{field_name.lower()}-select-all-btn', n_clicks=0, color='primary', size='sm', style={"margin-right": "10px"}),
                        dbc.Button("Clear", id=f'{field_name.lower()}-clear-btn', n_clicks=0, color='secondary', size='sm')
                    ], style={"margin-top": "10px"}),
                    dcc.Checklist(
                        id=f'{field_name.lower()}-filter-options',
                        options=[{'label': i, 'value': i} for i in sorted(field_values)],
                        value=[],  # Empty list means no filters selected (All)
                        labelStyle={'display': 'block'},
                        style={'height': '150px', 'overflowY': 'scroll'}
                    )
                ], id=f'{field_name.lower()}-basic-options')
            ]),
            id=collapse_id,
            is_open=False  # By default, collapse is closed
        ),
    ])


def create_date_filter_section(field_name):
    """Create a filter section for date data using DatePickerRange."""
    collapse_id = f'{field_name.lower()}-collapse'
    return html.Div([
        html.Div([
            html.Label(f'{field_name}', style={'cursor': 'pointer'}, id=f'{field_name.lower()}-toggle', className="filter-label"),
        ], style={"margin-bottom": "10px"}),

        dbc.Collapse(
            html.Div([
                dcc.DatePickerRange(
                    id=f'{field_name.lower()}-filter-options',
                    start_date_placeholder_text="Start Date",
                    end_date_placeholder_text="End Date",
                    display_format="YYYY-MM-DD",
                    style={'width': '95%'}
                )
            ]),
            id=collapse_id,
            is_open=False  # Initially collapsed
        )
    ])



def create_numeric_filter_section(field_name, field_values):
    """Create a filter section for numeric data (slider)."""
    collapse_id = f'{field_name.lower()}-collapse'
    min_val, max_val = min(field_values), max(field_values)

    return html.Div([
        html.Div([
            html.Label(f'{field_name}', style={'cursor': 'pointer'}, id=f'{field_name.lower()}-toggle', className="filter-label"),
        ], style={"margin-bottom": "10px"}),

        dbc.Collapse(
            html.Div([
                dcc.RangeSlider(
                    id=f'{field_name.lower()}-filter-options',
                    min=min_val,
                    max=max_val,
                    step=(max_val - min_val) / 100,  # Adjust the step size based on range
                    marks={int(i): str(int(i)) for i in range(int(min_val), int(max_val) + 1, int((max_val - min_val) / 5))},
                    value=[min_val, max_val],  # Default range
                    tooltip={"placement": "bottom", "always_visible": True},
                    style={'width': '95%'}
                )
            ]),
            id=collapse_id,
            is_open=False  # Initially collapsed
        )
    ])



def create_filter_section(filter_config, df):
    """Create the appropriate filter section based on the config."""
    field_name = filter_config['column']
    filter_type = filter_config['filter_type']

    if filter_type == 'dropdown':  # Categorical filter
        unique_values = df[field_name].dropna().unique()
        return create_categorical_filter_section(field_name, unique_values)

    elif filter_type == 'date':  # Date filter
        return create_date_filter_section(field_name)

    elif filter_type == 'numeric':  # Numeric filter
        numeric_values = df[field_name].dropna().values
        return create_numeric_filter_section(field_name, numeric_values)

    else:
        raise ValueError(f"Unknown filter type: {filter_type}")





# def create_filter_section(field_name, field_values):
#     # This ID will be used to toggle the visibility of the filter options (the collapsible section)
#     collapse_id = f'{field_name.lower()}-collapse'
#     return html.Div([
#         # The clickable label that will toggle the collapse
#         html.Div([
#             html.Label(f'{field_name}', style={'cursor': 'pointer'}, id=f'{field_name.lower()}-toggle', className="filter-label"),
#         ], style={"margin-bottom": "10px"}),
        
#         # The collapsible section that contains the dropdown and filter options
#         dbc.Collapse(
#             html.Div([
#                 dcc.Dropdown(
#                     id=f'{field_name.lower()}-filter-type',
#                     options=[{'label': 'Basic filtering', 'value': 'basic'}, {'label': 'Advanced filtering', 'value': 'advanced'}],
#                     value='basic',
#                     clearable=False,
#                     style={'width': '95%'}
#                 ),
#                 html.Div([
#                     html.Label("Search"),
#                     dcc.Input(id=f'{field_name.lower()}-search', type='text', placeholder="Search...", debounce=True),
#                     html.Div([
#                         dbc.Button("Select All", id=f'{field_name.lower()}-select-all-btn', n_clicks=0, color='primary', size='sm', style={"margin-right": "10px"}),
#                         dbc.Button("Clear", id=f'{field_name.lower()}-clear-btn', n_clicks=0, color='secondary', size='sm')
#                     ], style={"margin-top": "10px"}),
#                     dcc.Checklist(
#                         id=f'{field_name.lower()}-filter-options',
#                         options=[{'label': i, 'value': i} for i in sorted(field_values)],
#                         value=[],  # Empty list means no filters selected (All)
#                         labelStyle={'display': 'block'},
#                         style={'height': '150px', 'overflowY': 'scroll'}
#                     )
#                 ], id=f'{field_name.lower()}-basic-options')
#             ]),
#             id=collapse_id,
#             is_open=False  # By default, collapse is closed
#         ),
#     ])



# Function to generate the entire sidebar layout dynamically
# def create_sidebar_layout(df):
    
#     filter_sections = []
#     for col in df.columns:
#         unique_values = df[col].astype(str).unique()
#         filter_sections.append(create_filter_section(col, unique_values))
    
#     ret = [html.H2("Filters")]
#     for fsec in filter_sections:
#         ret.append(html.Hr())
#         ret.append(fsec)

#     return html.Div(ret, id='sidebar')

def create_sidebar_layout(df):
    """Generate the sidebar layout based on the config."""
    config = load_filter_config()

    filter_sections = []
    for filter_config in config['filters']:
        filter_section = create_filter_section(filter_config, df)
        filter_sections.append(filter_section)
    
    ret = [html.H2("Filters")]
    for fsec in filter_sections:
        ret.append(html.Hr())
        ret.append(fsec)

    return html.Div(ret)


# def create_sidebar_layout(df):
#     # Load the filter configuration
#     config = load_filter_config()

#     filter_sections = []
#     for filter_config in config['filters']:
#         col = filter_config['column']
#         unique_values = df[col].astype(str).unique()
#         filter_sections.append(create_filter_section(col, unique_values))
    
#     ret = [html.H2("Filters")]
#     for fsec in filter_sections:
#         ret.append(html.Hr())
#         ret.append(fsec)

#     return html.Div(ret)
