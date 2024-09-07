
# Builtin packages
from pathlib import Path
import time
import os
import datetime
import dateutil.parser
import math
from math import floor

# Third-party packages
import pandas as pd
from jira import JIRA


def get_from_jira(server: str="https://unisysbes.atlassian.net", save_local: bool=True) -> pd.DataFrame:
    return pull_from_jira_api(server, save_local)

def pull_from_jira_api(server: str="https://unisysbes.atlassian.net", save_local: bool=True) -> pd.DataFrame:
    """
    Pulls JIRA data from the specified server, processes, returns dataframe

    NOTE: This is essentially a git-safe copy-paste from the Jupyter Notebook
        `Updated JIRA FAT DEFECTS.ipynb`
        
    """

    print('pull_from_jira_api called')

    jiraOptions = {'server': server}

    jira = JIRA(
        options=jiraOptions, 
        basic_auth=(
            os.getenv('JIRA_USERNAME'), 
            os.getenv('JIRA_API_KEY'))
        )

    current_datetime = datetime.datetime.now()
    currentTS = current_datetime.timestamp()

    allfields = jira.fields()
    nameMap = {jira.field['name']: jira.field['id'] for jira.field in allfields}

    fieldnames = []
    data = []

    date_format = '%m/%d/%Y %I:%M %p'

    hours = "hours"
    minutes = "minutes"
    seconds = "seconds"
    days = "days"

    createdDateTS = None

    def format_elapsed_time(elapsed_seconds):
        elapsed_days = floor(elapsed_seconds / (60 * 60 * 24))
        elapsed_seconds -= elapsed_days * (60 * 60 * 24)
        elapsed_hours = floor(elapsed_seconds / (60 * 60))
        elapsed_seconds -= elapsed_hours * (60 * 60)
        elapsed_minutes = floor(elapsed_seconds / 60)
        elapsed_seconds -= elapsed_minutes * 60

        elapsed_time_str = ""
        if elapsed_days > 0:
            elapsed_time_str += f"{elapsed_days} {days}, "
        elapsed_time_str += f"{elapsed_hours} {hours}, {elapsed_minutes} {minutes}, {elapsed_seconds} {seconds}"
        
        return elapsed_time_str

    def fetchJiraTickets(startAt, pageNumber):
        global createdDateTS  
        for issue in jira.search_issues(jql_str='project = UAT AND issuetype = Bug AND affectedversion = "Release 0.12" ORDER BY created DESC', startAt=startAt, maxResults=100, expand='changelog'):
            formattedCreatedDate = dateutil.parser.parse(issue.fields.created).strftime(date_format)

            jiraItemDict = {"JIRA Key": issue.key, "Display Name": issue.fields.reporter.displayName, "Created Date": formattedCreatedDate}
            fieldnames.extend(["JIRA Key", "Display Name", "Created Date", "Details", "Priority", "Resolution", "Assignee", "Status", "Environment", "Root Cause", "Severity"])
            
            try:
                jiraItemDict["Details"] = issue.fields.summary
                jiraItemDict["Priority"] = issue.fields.priority.name
                jiraItemDict["Resolution"] = issue.fields.resolution
                jiraItemDict["Assignee"] = issue.fields.assignee.displayName
                jiraItemDict["Status"] = issue.fields.status.name
                jiraItemDict["Environment"] = issue.fields.customfield_10065.value
                jiraItemDict["Root Cause"] = issue.fields.customfield_10063.value
                jiraItemDict["Severity"] = issue.fields.customfield_10072.value
            except AttributeError:
                pass

            createdDate = dateutil.parser.parse(issue.fields.created)
            createdDateTS = createdDate.timestamp()
            elapsedTSSinceCreation = (currentTS - createdDateTS)

            fieldnames.append("Total Elapsed Time")

            jiraItemDict["Total Elapsed Time"] = format_elapsed_time(elapsedTSSinceCreation)

            i = 0
            data.append(jiraItemDict)
            historyRecords = issue.changelog.histories
            historyRecords.reverse()

            previousHistoryCreatedDate = None
            
            if historyRecords is not None:
                for history in historyRecords:
                    for item in history.items:
                        if item.field == 'status':
                            historyCreatedDate = dateutil.parser.parse(history.created)
                            
                            if (previousHistoryCreatedDate is None):
                                issueCreatedDate = dateutil.parser.parse(issue.fields.created)
                                dateTimeDiff = (historyCreatedDate.timestamp() - issueCreatedDate.timestamp())
                            else:
                                dateTimeDiff = (historyCreatedDate.timestamp() - previousHistoryCreatedDate.timestamp())

                            
                            if i == 1:
                                time_status_field = f"Time in Status {i}"
                            else:
                                time_status_field = f"Time In Status {i}"
                            
                            fieldnames.extend([time_status_field, f"Old Status {i}", f"New Status {i}", f"Changed By {i}", f"Changed Date {i}"])
                            
                            elapsedTimeInHours = dateTimeDiff / 3600  
                            jiraItemDict[time_status_field] = elapsedTimeInHours  

                            jiraItemDict[f"Old Status {i}"] = item.fromString
                            jiraItemDict[f"New Status {i}"] = item.toString
                            jiraItemDict[f"Changed By {i}"] = history.author.displayName
                            jiraItemDict[f"Changed Date {i}"] = dateutil.parser.parse(history.created).strftime(date_format)

                            i += 1
                            previousHistoryCreatedDate = historyCreatedDate
        return data


    jiraCount = jira.search_issues(jql_str='project = UAT AND issuetype = Bug AND affectedversion = "Release 0.12" ORDER BY created DESC', startAt=0, maxResults=0, json_result=True)
    totalJiraItems = jiraCount['total']
    print(f"Total Number of JIRA Items: {totalJiraItems}")
    recordsPerPage = 100
    totalPages = math.ceil(totalJiraItems/recordsPerPage)

    startAt = 0
    pageNumber = 1

    while pageNumber <= totalPages:
        print(f"Processing Page # {pageNumber}")
        data = fetchJiraTickets(startAt, pageNumber)
        pageNumber += 1
        startAt += 100


    fieldnames = list(dict.fromkeys(fieldnames))

    # Check if a previous dataset exists and load it
    if os.path.exists('JIRA_Complete_Data.xlsx'):
        #existing_data = pd.read_excel('JIRA_Complete_Data.xlsx')
        #new_data = pd.DataFrame(data, columns=fieldnames)
        # Concatenate the existing data with the new data
        #combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset="JIRA Key", keep="last")
        combined_data = pd.DataFrame(data, columns=fieldnames)
    else:
        combined_data = pd.DataFrame(data, columns=fieldnames)

    print("Data processing complete.") 

    if save_local:
        #timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        combined_data.to_excel(f'JIRA_Complete_Data.xlsx', index=False)
        print("The file 'JIRA_Complete_Data.xlsx' has been updated.")

    return combined_data

def process_jira_data(df):
    # Process the Jira data for your dashboard needs, e.g., create contributor columns
    df['Created Date'] = pd.to_datetime(df['Created Date'])
    min_date = df['Created Date'].min().date()
    max_date = df['Created Date'].max().date()

    assignee_counts = df['Assignee'].value_counts().reset_index()
    assignee_counts.columns = ['Person', 'Assignee Count']

    contributor_columns = [f'Changed By {i}' for i in range(76)]
    contributor_df = pd.melt(df, id_vars=['JIRA Key'], value_vars=contributor_columns, value_name='Contributor')
    contributor_df = contributor_df.drop_duplicates(subset=['JIRA Key', 'Contributor'])
    contributor_df = contributor_df.merge(df[['JIRA Key', 'Assignee']], on='JIRA Key', how='left')
    contributor_df = contributor_df[contributor_df['Contributor'] != contributor_df['Assignee']]

    contributor_counts = contributor_df['Contributor'].value_counts().reset_index()
    contributor_counts.columns = ['Person', 'Contributor Count']

    merged_people = pd.merge(assignee_counts, contributor_counts, how='outer', on='Person').fillna(0)

    return df, merged_people, min_date, max_date
