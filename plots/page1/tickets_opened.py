import pandas as pd
import plotly.express as px

def create_tickets_opened_chart(data: pd.DataFrame):

    # if data is None:
    #     return px.bar(title='No data available. Fetch data to see the graph.')

    # # Convert JSON data back to a dataframe
    # data = pd.read_json(data, orient='split')

    # TODO error handling


    # Process data for the chart
    # start_date = pd.to_datetime(start_date)
    # end_date = pd.to_datetime(end_date)
    data['Created Date'] = pd.to_datetime(data['Created Date'])
    tickets_per_day = data.groupby([data['Created Date'].dt.date, 'Priority']).size().reset_index(name='Count')
    tickets_per_day.rename(columns={'Created Date': 'Date'}, inplace=True)

    # Filter data based on selected priorities and date range
    tickets_per_day['Date'] = pd.to_datetime(tickets_per_day['Date'])
    # filtered_tickets = tickets_per_day[
    #     (tickets_per_day['Priority'].isin(selected_priorities)) &
    #     (tickets_per_day['Date'] >= start_date) &
    #     (tickets_per_day['Date'] <= end_date)
    # ]
    filtered_tickets = tickets_per_day

    start_date = filtered_tickets['Date'].min()
    end_date = filtered_tickets['Date'].max()

    # Calculate dynamic height based on the number of days in the selected range
    n_days = (end_date - start_date).days
    height = (n_days / 250) * 5000
    try:
        height = int(height)
        height = max(600, height)
    except:
        height = 600

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
