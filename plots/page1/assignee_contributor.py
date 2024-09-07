import pandas as pd
import plotly.express as px

def create_assignee_contributor_chart(data: pd.DataFrame):
    # if data is None:
    #     return px.bar(title='No data available. Fetch data to see the graph.')

    # # Convert JSON data back to a dataframe
    # data = pd.read_json(data, orient='split')

    # TODO error handling

    try:
        # Process data for the chart (same as before)
        assignee_counts = data['Assignee'].value_counts().reset_index()
        assignee_counts.columns = ['Person', 'Assignee Count']

        contributor_columns = [f'Changed By {i}' for i in range(76)]
        contributor_df = pd.melt(data, id_vars=['JIRA Key'], value_vars=contributor_columns, value_name='Contributor')
        contributor_df = contributor_df.drop_duplicates(subset=['JIRA Key', 'Contributor'])
        contributor_df = contributor_df.merge(data[['JIRA Key', 'Assignee']], on='JIRA Key', how='left')
        contributor_df = contributor_df[contributor_df['Contributor'] != contributor_df['Assignee']]

        contributor_counts = contributor_df['Contributor'].value_counts().reset_index()
        contributor_counts.columns = ['Person', 'Contributor Count']

        # Merge assignee and contributor counts
        merged_counts = pd.merge(assignee_counts, contributor_counts, how='outer', on='Person').fillna(0)
        merged_counts = merged_counts.sort_values(by=['Assignee Count', 'Person'], ascending=True)

        # # Filter the data based on selected people
        # if selected_people:
        #     merged_counts = merged_counts[merged_counts['Person'].isin(selected_people)]
        # else:
        #     # If no people are selected, return an empty figure
        #     return px.bar(title="No assignees/contributors selected")

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
    
    except Exception as err:
        return px.bar(title='Error')