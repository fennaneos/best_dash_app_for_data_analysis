import requests
import pandas as pd

# Define the API URL
api_url = "https://bfmrestapi.tnz.amadeus.net/SSP-RGW/DbQueryRequest/Requests/ESGNMRequest/resultset"

# Define parameters for the request
params = {
    'kpiType': 'Evolution',
    'kpiName': 'ResponseTime',
    'viewName': 'Engine',
    'customerAlias': 'AC0',
    'txn_search_by': 'message',
    'message': 'CALRQT',
    'timeScale': '3600',
    'dateFrom': '2024-09-03',
    'dateTo': '2024-09-10',
    'technical_details': True,
    'graphSelection': {'NbTransactions', 'AvgAAMCorpoRT', 'AvgAAMRT', 'AvgDPRT', 'AvgEngineCPU', 'AvgEngineRT', 'AvgJSRT', 'AvgTransactionRT', 'AvgAAMEligibilityRT', 'AvgAAMIntegratedRT', 'AvgAVERT', 'AvgSWERT'}  # Example KPI selection
}

# Make the GET request
response = requests.get(api_url, params=params, verify=False)

# Check response status
if response.status_code == 200:
    data = response.json()
    
    # Convert response data to DataFrame for easier manipulation
    df = pd.DataFrame(data).T  # Transpose if needed, depending on the structure
    print(df)
else:
    print(f"Error: {response.status_code}")
    df = pd.DataFrame()  # Empty DataFrame if there's an error
