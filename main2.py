import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from pathlib import Path

# Load the data
df = pd.read_csv(Path('.') / 'data' / 'JIRA_Complete_Data_CSV.csv', encoding="ISO-8859-1")

# Convert 'Created Date' to datetime
df['Created Date'] = pd.to_datetime(df['Created Date'], format='%m/%d/%Y %I:%M %p')

min_date = df['Created Date'].min().date()
max_date = df['Created Date'].max().date()
n_days = (max_date - min_date).days



# Group data by 'Created Date' and 'Priority' and count tickets
tickets_per_day = df.groupby([df['Created Date'].dt.date, 'Priority']).size().reset_index(name='Count')
tickets_per_day.rename(columns={'Created Date': 'Date'}, inplace=True)

# Get the list of columns that have contributors ("Changed By 0" to "Changed By 75")
contributor_columns = [f'Changed By {i}' for i in range(76)]

# Get the count of tickets where each person is the assignee
assignee_counts = df['Assignee'].value_counts().reset_index()
assignee_counts.columns = ['Person', 'Assignee Count']

# Melt the data to get a long format of contributors
contributor_df = pd.melt(df, id_vars=['JIRA Key'], value_vars=contributor_columns, value_name='Contributor')

# Drop duplicate contributors for each ticket to ensure each person is counted only once per ticket
contributor_df = contributor_df.drop_duplicates(subset=['JIRA Key', 'Contributor'])

# Merge with the original dataframe to associate each ticket with its assignee
contributor_df = contributor_df.merge(df[['JIRA Key', 'Assignee']], on='JIRA Key', how='left')

# Exclude rows where the contributor is also the assignee for the same ticket
contributor_df = contributor_df[contributor_df['Contributor'] != contributor_df['Assignee']]

# Get the count of tickets where each person is a contributor (distinct tickets)
contributor_counts = contributor_df['Contributor'].value_counts().reset_index()
contributor_counts.columns = ['Person', 'Contributor Count']


# Merge the two counts
merged_counts = pd.merge(assignee_counts, contributor_counts, how='outer', on='Person').fillna(0)

# Initialize the app
app = dash.Dash(__name__)
app.title = "Jira Dashboard"
app.config.suppress_callback_exceptions = True

# Layout for the navigation bar
navbar = html.Div([
    dcc.Link('Page 1 | ', href='/'),
    dcc.Link('Page 2', href='/page-2'),
])

# Page 1 layout
page_1_layout = html.Div([
    navbar,
    html.H1('P1: Tickets Opened and Time in Status'),
    # Add your graphs here (like tickets opened, time in status)
    dcc.Graph(id='tickets-opened-graph'),
    dcc.Graph(id='time-in-status-graph')
])




# Page 2 layout (modification)
page_2_layout = html.Div([
    navbar,
    html.H1('P2: Priority vs Day | Assignee vs Contributor'),

    # Left side with static labels, dropdown filter, and scrollable chart
    html.Div([
        # Static title and axis labels (non-scrollable)
        html.Div([
            html.H3("Tickets Opened per Day by Priority"),
        ], style={'textAlign': 'center'}),

        # Date Picker for filtering date range
        dcc.DatePickerRange(
            id='date-picker-range',
            min_date_allowed=min_date,  # Minimum date in the dataset
            max_date_allowed=max_date,  # Maximum date in the dataset
            start_date=min_date,  # Default to the full range
            end_date=max_date,
            display_format='YYYY-MM-DD',  # Display format of the date
            style={'marginBottom': '10px'}
        ),
        
        # Priority Filter Dropdown
        html.Div(
            [
                dcc.Dropdown(
                    id='priority-filter',
                    options=[{'label': priority, 'value': priority} for priority in ['Highest', 'High', 'Medium', 'Low']],
                    value=['Highest', 'High', 'Medium', 'Low'],  # Default to all priorities selected
                    multi=True,
                    placeholder="Select priorities",
                )
            ], style={'height': '100px', 'marginBottom': '10px'}),

        # Scrollable container for the graph only
        html.Div([
            dcc.Graph(id='tickets-opened-priority-chart')
        ], style={'height': '600px', 'overflowY': 'scroll'})  # Scrollable container for chart
    ], style={'width': '50%', 'display': 'inline-block'}),

    # Right side with static labels, filter buttons, scrollable dropdown filter, and scrollable chart
    html.Div([
        # Static title and axis labels (non-scrollable)
        html.Div([
            html.H3("Assignee vs Contributor Counts"),
        ], style={'textAlign': 'center'}),

        # Filter buttons
        html.Div([
            html.Button('Select All', id='select-all-btn', n_clicks=0),
            html.Button('Deselect All', id='deselect-all-btn', n_clicks=0),
        ], style={'textAlign': 'center', 'marginBottom': '10px'}),

        # Scrollable container for the Person Filter Dropdown
        html.Div([
            dcc.Dropdown(
                id='person-filter',
                options=[{'label': person, 'value': person} for person in merged_counts['Person']],
                #value=[],  # No default selection
                value=merged_counts['Person'].tolist(),  # Select all by default
                multi=True,
                placeholder="Select assignees/contributors",
                searchable=True,
            ),
        ], style={'height': '100px', 'overflowY': 'scroll', 'marginBottom': '10px'}),  # Scrollable container for dropdown

        # Scrollable container for the graph only
        html.Div([
            dcc.Graph(id='assignee-contributor-bar-chart')
        ], style={'height': '600px', 'overflowY': 'scroll'})  # Scrollable container for chart
    ], style={'width': '50%', 'display': 'inline-block'})

])



# Main layout for navigation
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback to handle page navigation
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
    Output('person-filter', 'value'),
    [Input('select-all-btn', 'n_clicks'),
     Input('deselect-all-btn', 'n_clicks')],
    [Input('person-filter', 'value')],
    prevent_initial_call=True
)
def select_deselect_all(select_all_clicks, deselect_all_clicks, current_selection):
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

    return dash.no_update  # No update for normal dropdown behavior

# Sort the merged_counts DataFrame by 'Assignee Count' in descending order
merged_counts = merged_counts.sort_values(by=['Assignee Count', 'Person'], ascending=False)

@app.callback(
    Output('assignee-contributor-bar-chart', 'figure'),
    [Input('person-filter', 'value')]
)
def update_assignee_contributor_chart(selected_people):
    # Filter data based on selected people
    filtered_data = merged_counts[merged_counts['Person'].isin(selected_people)]
    filtered_data = filtered_data.sort_values(by=['Assignee Count'], ascending=True)

    n_people = len(set(filtered_data['Person']))
    height = (n_people / 120) * 5000
    height = max(600, int(height))

    # Create horizontal grouped bar chart
    fig = px.bar(
        filtered_data,
        y='Person',
        x=['Contributor Count', 'Assignee Count'],
        orientation='h',  # Horizontal bars
        barmode='group',  # Grouped bars
        text_auto=True,  # Show text after bars
        color_discrete_map={
            'Assignee Count': '#006400',
            'Contributor Count': '#93c47d'
        }
    )

    # Update layout to make the chart height very tall to allow scrolling
    fig.update_layout(
        height=height,  # Make the chart really tall (can adjust as needed)
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=True
    )

    return fig






@app.callback(
    Output('tickets-opened-priority-chart', 'figure'),
    [Input('priority-filter', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_tickets_opened_priority_chart(selected_priorities, start_date, end_date):
    # Convert start and end dates to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    tickets_per_day['Date'] = pd.to_datetime(tickets_per_day['Date'])

    # Filter data based on selected priorities and date range
    filtered_tickets = tickets_per_day[
        (tickets_per_day['Priority'].isin(selected_priorities)) &
        (tickets_per_day['Date'] >= start_date) &
        (tickets_per_day['Date'] <= end_date)
    ]

    n_days = (end_date - start_date).days
    height = (n_days/250) * 5000
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
        orientation='h',  # Horizontal bars
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
