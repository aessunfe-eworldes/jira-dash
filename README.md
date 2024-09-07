# jira-dash

jira-dash is a dashboard for visualizing Jira tickets & metrics, and identifying slowdowns

# Current Status (2024-09-06 19:00 HST)

- `main5.py` is the most up-to-date file

- Page 1 contains the plots that were previously on page 2 of `main4.py`

- Some preliminary filters have been implemented, with more to come. Power BI-style filter logic.

- Framework is flexible, with centralized filtered data, meaning adding more plots will be easier

# Usage

- Clone the repository
- Create a virtual environment `python -m venv venv`
- Activate the environment `source venv/bin/activate` or `.\venv\Scripts\activate`
- Upgrade `pip`: `pip install --upgrade pip`
- Install dependencies: `pip install -r requirements.txt`
- Ensure the presence of a file called `.env` (hidden file) with `JIRA_USERNAME=...` and `JIRA_API_KEY=...` lines
- Run the program: `python main5.py`
- Select an **Excel** file with the data to upload, or select the first option from the dropdown and hit `Fetch` button

# Next Steps

- [DONE] Implement actual Jira fecthing using jira Python API
- [DONE] Add basic filter logic
- Add more filters
- Add Gantt chart on a new page, configurable by person
- Add Lance's specific charts
- Add Drill-Through charts
- Add other API endpoints, to switch between projects
