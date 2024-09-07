
# Third-party imports

from dash import dcc, html


def page1_layout(tickets_chart, assignee_chart):
    return html.Div([
        html.Div([
            html.Div([
                html.H3("Tickets Opened per Day by Priority"),
            ], style={'textAlign': 'center'}),

            html.Div([
                dcc.Graph(id='tickets-opened-priority-chart', figure=tickets_chart)
            ], style={'height': '600px', 'overflowY': 'scroll'})
        ], style={'width': '50%', 'display': 'inline-block'}),

        # Right side (Assignee vs Contributor)
        html.Div([
            html.Div([
                html.H3("Assignee vs Contributor Counts"),
            ], style={'textAlign': 'center'}),

            html.Div([
                dcc.Graph(id='assignee-contributor-bar-chart', figure=assignee_chart)
            ], style={'height': '600px', 'overflowY': 'scroll'})
        ], style={'width': '50%', 'display': 'inline-block'})
    ])
