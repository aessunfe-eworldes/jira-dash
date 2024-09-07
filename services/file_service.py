
import pandas as pd
import base64
import io

def process_uploaded_file(file_contents, file_name):
    content_type, content_string = file_contents.split(',')
    decoded = base64.b64decode(content_string)

    # Process CSV or Excel files
    if file_name.endswith('.csv'):
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        except UnicodeDecodeError:
            df = pd.read_csv(io.StringIO(decoded.decode('ISO-8859-1')))
    elif file_name.endswith('.xlsx'):
        df = pd.read_excel(io.BytesIO(decoded))
    else:
        raise ValueError(f"Unsupported file type: {file_name}")

    return df
