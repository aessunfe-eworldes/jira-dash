# Python standard library imports
import io
import base64
import json
from datetime import datetime

# Third-party imports
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, MATCH, ALL
import plotly.express as px
import dash_bootstrap_components as dbc

# Local imports
from services.jira_service import get_from_jira
from services.config_service import load_filter_config
from components.topbar import topbar
from components.sidebar import create_filter_section, sidebar
from components.content import content
from components.page1.page1_layout import page1_layout

from plots.page1.assignee_contributor import create_assignee_contributor_chart
from plots.page1.tickets_opened import create_tickets_opened_chart

# Initialize the Dash app with external stylesheets
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout for the entire app
app.layout = html.Div(
    [
        dcc.Store(id='stored-filters'),  # Store to retain filter states
        dcc.Store(id='raw-data-store'),  # Store for raw data
        dcc.Store(id='filtered-data-store'),  # Store for filtered data
        dcc.Location(id="url"),  # URL bar to handle page navigation
        topbar,
        dbc.Button("Toggle Sidebar", id="btn_sidebar", n_clicks=0, style=dict(display='none')),  # Hidden
        sidebar,
        dbc.Row([
            dbc.Col(dbc.Button("Page 1", href="/page-1", color="primary"), width=2),
            dbc.Col(dbc.Button("Page 2", href="/page-2", color="secondary"), width=2),
        ]),
        content,
    ]
)

@app.callback(
    [Output("raw-data-store", "data"),
     Output("timestamp-display", "children"),
     Output("sidebar", "children")],
    [Input("fetch-jira-btn", "n_clicks"),
     Input("file-upload", "contents")],
    [State("jira-server-url", "value"),
     State("file-upload", "filename")]
)
def load_data_from_source(jira_clicks, file_contents, server_url, filename):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # Determine the triggered input
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    # Initialize the return variables
    df = None
    timestamp_msg = None

    if triggered_input == "fetch-jira-btn" and server_url:
        # Fetch from JIRA
        df = get_from_jira(server_url)  # Assuming this function exists and returns a DataFrame
        timestamp_msg = f"Jira data fetched at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    elif triggered_input == "file-upload" and file_contents:
        # Handle file upload
        content_type, content_string = file_contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif filename.endswith(".xlsx"):
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return dash.no_update, "Unsupported file type", dash.no_update
        except Exception as e:
            return dash.no_update, f"Error loading file: {str(e)}", dash.no_update

        timestamp_msg = f"Local file loaded at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {filename}"

    if df is None:
        raise dash.exceptions.PreventUpdate

    # Convert dataframe to JSON for storing
    df['Created Date'] = pd.to_datetime(df['Created Date'])
    filter_config = load_filter_config()

    # Generate the sidebar based on the config file and data
    sidebar_layout = [html.H1('Filters')]
    for filter_item in filter_config['filters']:
        col = filter_item['column']
        if col == 'Person':
            columns = ['Assignee', *[f'Changed By {x}' for x in range(76)]]
            values = pd.concat([pd.Series(df[col].dropna().unique()) for col in columns])
            values = sorted(values.unique())
        else:
            values = df[col].dropna().unique()
        filter_section = create_filter_section(col, values)
        sidebar_layout.append(html.Hr())
        sidebar_layout.append(filter_section)

    return df.to_json(date_format='iso', orient='split'), timestamp_msg, sidebar_layout

# Callback to update the content based on URL and filters
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname"),
     Input('filtered-data-store', 'data')]
)
def render_page_content(pathname, filtered_data_json):
    if filtered_data_json is None:
        raise dash.exceptions.PreventUpdate
    filtered_df = pd.read_json(filtered_data_json, orient='split')

    if pathname == "/" or pathname == "/page-1":

        # pie_fig = px.pie(filtered_df, names='Priority', title='Priority Distribution')
        ticket_chart = create_tickets_opened_chart(filtered_df)
        assignee_chart = create_assignee_contributor_chart(filtered_df)
        return page1_layout(ticket_chart, assignee_chart)
        #return html.Div([dcc.Graph(figure=pie_fig)])
    elif pathname == "/page-2":
        bar_fig = px.bar(filtered_df, x='Assignee', y='JIRA Key', title='Assignee-wise JIRA Tickets', barmode='group')
        return html.Div([dcc.Graph(figure=bar_fig)])
    else:
        return html.Div([html.H3("404: Page Not Found")])

# Callback to apply filters and store filtered data
@app.callback(
    Output("filtered-data-store", "data"),
    [Input({'type': 'filter-options', 'index': ALL}, 'value')],
    [State('raw-data-store', 'data')]
)
def apply_filters(filter_values, raw_data_json):
    if raw_data_json is None:
        raise dash.exceptions.PreventUpdate

    df = pd.read_json(raw_data_json, orient='split')
    filter_config = load_filter_config()

    for i, filter_item in enumerate(filter_config['filters']):
        column = filter_item['column']
        values = filter_values[i]
        # Custom filter for "Person"
        if column == 'Person':
            columns = ['Assignee', *[f'Changed By {x}' for x in range(76)]]
            tmp_df = df[df[columns].apply(lambda row: row.isin(values).any(), axis=1)]
            if len(tmp_df):
                df = tmp_df
        else:
            if values:
                df = df[df[column].isin(values)]

    return df.to_json(date_format='iso', orient='split')

# Toggle Collapse callback (handles expanding/collapsing filter sections)
@app.callback(
    Output({'type': 'filter-collapse', 'index': MATCH}, 'is_open'),
    [Input({'type': 'filter-toggle', 'index': MATCH}, 'n_clicks')],
    [State({'type': 'filter-collapse', 'index': MATCH}, 'is_open')]
)
def toggle_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


# Callback to toggle the visibility of the sidebar
@app.callback(
    Output("sidebar", "style"),
    [Input("btn_sidebar", "n_clicks")],
    [State("sidebar", "style")]
)
def toggle_sidebar(n_clicks, style):
    if n_clicks and style.get("display") == "none":
        style["display"] = "block"
    elif n_clicks:
        style["display"] = "none"
    return style

# Update filters dynamically (handles search, select all, clear functionality)
@app.callback(
    [Output({'type': 'filter-options', 'index': ALL}, 'options'),
     Output({'type': 'filter-options', 'index': ALL}, 'value'),
     Output({'type': 'select-all-btn', 'index': ALL}, 'n_clicks'),
     Output({'type': 'clear-btn', 'index': ALL}, 'n_clicks')],
    [Input({'type': 'search', 'index': ALL}, 'value'),
     Input({'type': 'select-all-btn', 'index': ALL}, 'n_clicks'),
     Input({'type': 'clear-btn', 'index': ALL}, 'n_clicks')],
    [State({'type': 'filter-options', 'index': ALL}, 'value'),
     State('raw-data-store', 'data')]
)
def update_filters(search_values, select_all_clicks, clear_clicks, current_values, raw_data_json):
    if raw_data_json is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    df = pd.read_json(raw_data_json, orient='split')
    filter_config = load_filter_config()

    updated_options = []
    updated_values = []
    reset_select_all_clicks = [0] * len(filter_config['filters'])  # Reset select all clicks
    reset_clear_clicks = [0] * len(filter_config['filters'])  # Reset clear clicks

    for i, filter_item in enumerate(filter_config['filters']):
        column = filter_item['column']
        if column == 'Person':
            columns = ['Assignee', *[f'Changed By {x}' for x in range(76)]]
            unique_values = pd.concat([pd.Series(df[col].dropna().unique()) for col in columns])
            unique_values_sorted = sorted(unique_values.unique())
            full_options = [{'label': str(val), 'value': str(val)} for val in unique_values_sorted]
        else:
            full_options = [{'label': str(val), 'value': str(val)} for val in sorted(df[column].dropna().unique())]

        # Apply search filter
        search_value = search_values[i]
        if search_value:
            filtered_options = [opt for opt in full_options if search_value.lower() in opt['label'].lower()]
        else:
            filtered_options = full_options

        # Handle Select All
        if select_all_clicks[i] > 0:
            selected_values = [opt['value'] for opt in filtered_options]
            reset_select_all_clicks[i] = 0  # Reset after selecting all
        # Handle Clear
        elif clear_clicks[i] > 0:
            selected_values = []
            reset_clear_clicks[i] = 0  # Reset after clearing
        else:
            selected_values = current_values[i]  # Keep current selections

        updated_options.append(filtered_options)
        updated_values.append(selected_values)

    return updated_options, updated_values, reset_select_all_clicks, reset_clear_clicks


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
