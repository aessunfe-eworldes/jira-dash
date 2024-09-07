
from dash import dcc, html
from layouts.navbar import navbar
from projects import PROJECTS

# Page 2 layout
page_2_layout = html.Div([
    navbar,
    html.H1('P2: Priority vs Day | Assignee vs Contributor'),

    # Filters section
    html.Div(id='dynamic-filters'),

    # Dropdown to select project URL or load from local file
    html.Div([
        dcc.Dropdown(
            id='project-selector',
            options=[{'label': key, 'value': value} for key, value in PROJECTS.items()],
            placeholder="Select a project or load from local file"
        )
    ], style={'width': '50%', 'marginBottom': '10px'}),

    # File picker for local file upload (hidden until "Load from local file" is selected)
    html.Div([
        dcc.Upload(
            id='file-upload',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select a File')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'marginBottom': '10px'
            },
            multiple=False
        ),
        # Visual feedback after file is uploaded
        html.Div(id='upload-feedback', style={'textAlign': 'center', 'marginTop': '10px'})
    ], id='file-upload-container', style={'display': 'none'}),  # Hidden by default

    # Button to trigger Jira data fetch or load from local file
    html.Div([
        html.Button('Fetch Data', id='fetch-data-btn', n_clicks=0),
    ], style={'textAlign': 'center', 'marginBottom': '10px'}),
    dcc.Loading(
        id='loading-fetch',
        type='default',
        children=html.Div(id='loading-output')
    ),
    # Store fetched Jira data
    dcc.Store(id='jira-data-store'),

    # Left side (Priority vs Day)
    html.Div([
        html.Div([
            html.H3("Tickets Opened per Day by Priority"),
        ], style={'textAlign': 'center'}),

        dcc.DatePickerRange(
            id='date-picker-range',
            min_date_allowed=None,  # These will be updated after data is fetched or loaded
            max_date_allowed=None,
            start_date=None,
            end_date=None,
            display_format='YYYY-MM-DD',
            style={'marginBottom': '10px'}
        ),
        
        dcc.Dropdown(
            id='priority-filter',
            options=[{'label': priority, 'value': priority} for priority in ['Highest', 'High', 'Medium', 'Low']],
            value=['Highest', 'High', 'Medium', 'Low'],
            multi=True,
            placeholder="Select priorities",
        ),
        html.Div([
            dcc.Graph(id='tickets-opened-priority-chart')
        ], style={'height': '600px', 'overflowY': 'scroll'})
    ], style={'width': '50%', 'display': 'inline-block'}),

    # Right side (Assignee vs Contributor)
    html.Div([
        html.Div([
            html.H3("Assignee vs Contributor Counts"),
        ], style={'textAlign': 'center'}),

        html.Div([
            html.Button('Select All', id='select-all-btn', n_clicks=0),
            html.Button('Deselect All', id='deselect-all-btn', n_clicks=0),
        ], style={'textAlign': 'center', 'marginBottom': '10px'}),

        html.Div([
            dcc.Dropdown(
                id='person-filter',
                options=[],  # Updated dynamically
                value=[],
                multi=True,
                placeholder="Select assignees/contributors",
                searchable=True,
            ),
        ], style={'height': '100px', 'overflowY': 'scroll', 'marginBottom': '10px'}),
        html.Div([
            dcc.Graph(id='assignee-contributor-bar-chart')
        ], style={'height': '600px', 'overflowY': 'scroll'})
    ], style={'width': '50%', 'display': 'inline-block'})
])
