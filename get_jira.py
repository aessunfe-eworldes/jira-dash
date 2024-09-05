from pathlib import Path
import time
import pandas as pd

def get_jira_data():
    time.sleep(10)
    df = pd.read_csv(Path('.') / 'data' / 'JIRA_Complete_Data_CSV.csv', encoding="ISO-8859-1")
    return df
