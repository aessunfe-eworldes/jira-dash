import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from get_jira import get_jira_data  # Import the function to fetch Jira data

# Initialize the app
app = dash.Dash(__name__)
app.title = "Jira Dashboard"
app.config.suppress_callback_exceptions = True

# Layout for the navigation bar
navbar = html.Div([
    dcc.Link('Page 1 | ', href='/'),
    dcc.Link('Page 2', href='/page-2'),
])

# Page 1 layout (unchanged)
page_1_layout = html.Div([
    navbar,
    html.H1('P1: Tickets Opened and Time in Status'),
    dcc.Graph(id='tickets-opened-graph'),
    dcc.Graph(id='time-in-status-graph')
])

# Page 2 layout with Fetch button, loading spinner, and graphs
page_2_layout = html.Div([
    navbar,
    html.H1('P2: Priority vs Day | Assignee vs Contributor'),

    # Button to trigger Jira data fetch and loading output
    html.Div([
        html.Button('Fetch Latest Jira Data', id='fetch-data-btn', n_clicks=0),
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
            min_date_allowed=None,  # These will be updated after data is fetched
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
                options=[],
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

# Main layout for navigation
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Navigation callback
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/page-2':
        return page_2_layout
    else:
        return page_1_layout

@app.callback(
    [Output('jira-data-store', 'data'),
     Output('loading-output', 'children'),
     Output('date-picker-range', 'min_date_allowed'),
     Output('date-picker-range', 'max_date_allowed'),
     Output('date-picker-range', 'start_date'),
     Output('date-picker-range', 'end_date'),
     Output('person-filter', 'options')],
    Input('fetch-data-btn', 'n_clicks')
)
def fetch_jira_data(n_clicks):
    if n_clicks > 0:
        # Fetch Jira data using the imported function
        df = get_jira_data()  # Assume this returns a pandas dataframe

        # Process the data and store it
        df['Created Date'] = pd.to_datetime(df['Created Date'])
        min_date = df['Created Date'].min().date()
        max_date = df['Created Date'].max().date()

        # Convert dataframe to JSON format to store in dcc.Store
        jira_data_json = df.to_json(date_format='iso', orient='split')

        # Prepare options for person filter based on assignee and contributor
        assignee_counts = df['Assignee'].value_counts().reset_index()
        assignee_counts.columns = ['Person', 'Assignee Count']

        contributor_columns = [f'Changed By {i}' for i in range(76)]
        contributor_df = pd.melt(df, id_vars=['JIRA Key'], value_vars=contributor_columns, value_name='Contributor')
        contributor_df = contributor_df.drop_duplicates(subset=['JIRA Key', 'Contributor'])
        contributor_df = contributor_df.merge(df[['JIRA Key', 'Assignee']], on='JIRA Key', how='left')
        contributor_df = contributor_df[contributor_df['Contributor'] != contributor_df['Assignee']]

        contributor_counts = contributor_df['Contributor'].value_counts().reset_index()
        contributor_counts.columns = ['Person', 'Contributor Count']

        # Merge assignee and contributor counts, ensuring the index is a column
        merged_people = pd.merge(assignee_counts, contributor_counts, how='outer', on='Person').fillna(0)

        # Create options for the dropdown
        person_options = [{'label': person, 'value': person} for person in merged_people['Person']]

        return jira_data_json, 'Data fetch complete!', min_date, max_date, min_date, max_date, person_options

    return dash.no_update, 'Click the button to fetch data', None, None, None, None, []


@app.callback(
    Output('person-filter', 'value'),
    [Input('select-all-btn', 'n_clicks'),
     Input('deselect-all-btn', 'n_clicks'),
     Input('jira-data-store', 'data')],
    prevent_initial_call=True
)
def select_deselect_all(select_all_clicks, deselect_all_clicks, jira_data_json):
    if jira_data_json is None:
        return []

    # Convert JSON data back to a dataframe
    jira_data = pd.read_json(jira_data_json, orient='split')

    # Process data to get the merged counts
    assignee_counts = jira_data['Assignee'].value_counts().reset_index()
    assignee_counts.columns = ['Person', 'Assignee Count']

    # Handle contributors and merging logic
    contributor_df = pd.melt(jira_data, id_vars=['JIRA Key'], value_vars=[f'Changed By {i}' for i in range(76)], value_name='Contributor')
    contributor_df = contributor_df.drop_duplicates(subset=['JIRA Key', 'Contributor'])
    contributor_df = contributor_df.merge(jira_data[['JIRA Key', 'Assignee']], on='JIRA Key', how='left')
    contributor_df = contributor_df[contributor_df['Contributor'] != contributor_df['Assignee']]

    contributor_counts = contributor_df['Contributor'].value_counts().reset_index()
    contributor_counts.columns = ['Person', 'Contributor Count']

    # Merge the two counts
    merged_counts = pd.merge(assignee_counts, contributor_counts, how='outer', on='Person').fillna(0)

    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'select-all-btn':
        # Return all people when 'Select All' is clicked
        return merged_counts['Person'].tolist()
    elif button_id == 'deselect-all-btn':
        # Clear the selection when 'Deselect All' is clicked
        return []

    return dash.no_update


@app.callback(
    Output('assignee-contributor-bar-chart', 'figure'),
    [Input('person-filter', 'value'),
     Input('jira-data-store', 'data')]
)
def update_assignee_contributor_chart(selected_people, jira_data_json):
    if jira_data_json is None:
        return px.bar(title='No data available. Fetch data to see the graph.')

    # Convert JSON data back to a dataframe
    jira_data = pd.read_json(jira_data_json, orient='split')

    # Process data for the chart (same as before)
    assignee_counts = jira_data['Assignee'].value_counts().reset_index()
    assignee_counts.columns = ['Person', 'Assignee Count']

    contributor_columns = [f'Changed By {i}' for i in range(76)]
    contributor_df = pd.melt(jira_data, id_vars=['JIRA Key'], value_vars=contributor_columns, value_name='Contributor')
    contributor_df = contributor_df.drop_duplicates(subset=['JIRA Key', 'Contributor'])
    contributor_df = contributor_df.merge(jira_data[['JIRA Key', 'Assignee']], on='JIRA Key', how='left')
    contributor_df = contributor_df[contributor_df['Contributor'] != contributor_df['Assignee']]

    contributor_counts = contributor_df['Contributor'].value_counts().reset_index()
    contributor_counts.columns = ['Person', 'Contributor Count']

    # Merge assignee and contributor counts
    merged_counts = pd.merge(assignee_counts, contributor_counts, how='outer', on='Person').fillna(0)

    # Filter the data based on selected people
    if selected_people:
        merged_counts = merged_counts[merged_counts['Person'].isin(selected_people)]
    else:
        # If no people are selected, return an empty figure
        return px.bar(title="No assignees/contributors selected")

    # Create horizontal grouped bar chart
    fig = px.bar(
        merged_counts,
        y='Person',
        x=['Contributor Count', 'Assignee Count'],
        orientation='h',
        barmode='group',
        text_auto=True,
        color_discrete_map={
            'Assignee Count': '#006400',
            'Contributor Count': '#93c47d'
        }
    )

    # Update layout to make the chart height dynamic based on the number of people
    n_people = len(merged_counts)
    height = int(max(600, (n_people / 120) * 5000))
    
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=True
    )

    return fig


# Callback for the Tickets Opened per Day by Priority chart
@app.callback(
    Output('tickets-opened-priority-chart', 'figure'),
    [Input('priority-filter', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('jira-data-store', 'data')]
)
def update_tickets_opened_priority_chart(selected_priorities, start_date, end_date, jira_data_json):
    if jira_data_json is None:
        return px.bar(title='No data available. Fetch data to see the graph.')

    # Convert JSON data back to a dataframe
    jira_data = pd.read_json(jira_data_json, orient='split')

    # Process data for the chart
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    jira_data['Created Date'] = pd.to_datetime(jira_data['Created Date'])
    tickets_per_day = jira_data.groupby([jira_data['Created Date'].dt.date, 'Priority']).size().reset_index(name='Count')
    tickets_per_day.rename(columns={'Created Date': 'Date'}, inplace=True)

    # Filter data based on selected priorities and date range
    tickets_per_day['Date'] = pd.to_datetime(tickets_per_day['Date'])
    filtered_tickets = tickets_per_day[
        (tickets_per_day['Priority'].isin(selected_priorities)) &
        (tickets_per_day['Date'] >= start_date) &
        (tickets_per_day['Date'] <= end_date)
    ]

    # Calculate dynamic height based on the number of days in the selected range
    n_days = (end_date - start_date).days
    height = (n_days / 250) * 5000
    height = int(height)
    height = max(600, height)

    # Create the stacked horizontal bar chart
    fig = px.bar(
        filtered_tickets,
        y='Date',
        x='Count',
        color='Priority',
        text='Count',
        text_auto=True,
        orientation='h',
        category_orders={'Priority': ['Highest', 'High', 'Medium', 'Low'][::-1]},  # Order of stacking
        color_discrete_map={
            'Highest': '#ff0000',
            'High': '#ffa500',
            'Medium': '#ffff00',
            'Low': '#008000'
        }
    )

    # Update layout
    fig.update_layout(
        xaxis_title='Number of Tickets',
        yaxis_title='Date',
        yaxis=dict(
            dtick='D1'  # Set the tick interval to 1 day
        ),
        height=height,  # Make the chart tall for scrolling
        margin=dict(l=20, r=20, t=50, b=20),
        legend_title='Priority',
        barmode='stack'
    )

    fig.update_yaxes(tickformat='%a, %Y-%m-%d')  # Display date in YYYY-MM-DD format
    fig.update_traces(textposition='inside')  # Ensure text is always visible

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)