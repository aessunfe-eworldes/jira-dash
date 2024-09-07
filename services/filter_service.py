from dash import dcc, html
import pandas as pd

def generate_filters(df):
    """Dynamically generates filter components based on the dataset columns."""
    filters = []

    # Example filter for 'Assignee'
    if 'Assignee' in df.columns:
        assignees = df['Assignee'].dropna().unique().tolist()
        filters.append(html.Div([
            html.Label("Assignee"),
            dcc.Dropdown(
                id='assignee-filter',
                options=[{'label': assignee, 'value': assignee} for assignee in assignees],
                multi=True,
                placeholder="Select Assignees",
                style={'width': '100%'}
            )
        ]))

    # Example filter for 'Priority'
    if 'Priority' in df.columns:
        priorities = df['Priority'].dropna().unique().tolist()
        filters.append(html.Div([
            html.Label("Priority"),
            dcc.Dropdown(
                id='priority-filter',
                options=[{'label': priority, 'value': priority} for priority in priorities],
                multi=True,
                placeholder="Select Priorities",
                style={'width': '100%'}
            )
        ]))

    # Example filter for 'Created Date'
    if 'Created Date' in df.columns:
        filters.append(html.Div([
            html.Label("Date Range"),
            dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=df['Created Date'].min(),
                max_date_allowed=df['Created Date'].max(),
                start_date=df['Created Date'].min(),
                end_date=df['Created Date'].max(),
                display_format='YYYY-MM-DD',
                style={'width': '100%'}
            )
        ]))

    return filters
