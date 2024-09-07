

from dash import dcc, html
import dash_bootstrap_components as dbc

# Top bar with file upload and JIRA fetch
topbar = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.H2("Jira Quickview"), width=3),
                dbc.Col(
                    dcc.Dropdown(
                        id="jira-server-url",
                        options=[
                            {'label': 'https://unisysbes.atlassian.net', 'value': 'https://unisysbes.atlassian.net'},
                            {'label': 'Server 2', 'value': 'https://unisysbes.atlassian.net'},
                            {'label': 'Server 3', 'value': 'https://unisysbes.atlassian.net'}
                        ],
                        placeholder="Select JIRA Server",
                        style={'width': '100%'}
                    ),
                    width=3,
                ),
                dbc.Col(
                    dbc.Button("Fetch from JIRA", id="fetch-jira-btn", color="primary"),
                    width=2,
                ),
                dbc.Col(html.H3("or"), width=1, style={"text-align": "center"}),
                dbc.Col(
                    dcc.Upload(
                        id="file-upload",
                        children=html.Div([dbc.Button("Upload File", color="secondary")]),
                        multiple=False,
                    ),
                    width=3,
                ),
                dbc.Col(html.Div(id="timestamp-display"), width=3),
            ],
            className="my-2",
        ),
    ],
    style={"margin-right": "20%", "padding": "20px", "border-bottom": "1px solid #ccc"}
)