# jira-dash

jira-dash is a dashboard for visualizing Jira tickets & metrics, and identifying slowdowns

# Current Status (2024-09-04 17:00 HST)

- Page 1 is an empty placeholder

- `main2.py` reads a local copy of the file `JIRA_Complete_Data_CSV.csv`, which is simply the `JIRA_Complete_Data.xlsx` file exported as a CSV. 

- `main3.py` simulates fetching the Jira data and updating the charts with it, but does not have all the same formatting features as `main2.py` (e.g., sorting the assignee vs contributor chart by tickets assigned). 

# Next Steps

- Implement actual Jira fecthing using jira Python API
- Add Gantt chart on a third page, configurable by person
- Implement support for multiple API endpoints, to switch between projects
