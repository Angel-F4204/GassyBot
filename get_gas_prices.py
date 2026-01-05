import requests
import json
import os # need to read eia key from an environment variable
from dotenv import load_dotenv
load_dotenv()

headers = {"authorization": os.getenv("COLLECT_API_KEY"),
         "content-type" : "application/json"}
EIA_API_KEY= os.getenv("EIA_API_KEY", "").strip()
def get_gas_prices(state_name):
    url = "https://api.collectapi.com/gasPrice/allUsaPrice"
    response = requests.get(url, headers=headers)
    data = response.json()

    #handle api errors
    if not data.get("success"):
        return f"Error: {data.get('message', 'Unknown issue')}"
    

    #return all results
    for state in data.get("result",[]):
        if state["name"].lower() == state_name.lower():
            return(f" Gas Prices - {state_name}:\n"
                   f" Regular: ${state['gasoline']}\n"
                   f" MidGrade: ${state['midGrade']}\n"
                   f" Premium: ${state['premium']}\n"
                   f" Diesel: ${state['diesel']}\n\n"
                   f"🗺️ Map: https://www.google.com/maps/search/gas+stations+in+{state_name.replace(' ', '+')}")

    
    return f"State '{state_name}' not found."

#params = {"country": "USA", "city": "New York"}
if __name__ == "__main__": 
    print(get_gas_prices("New York"))


def get_eia_ny_weekly():
    if not EIA_API_KEY:
        return "EIA error: no API key set. Set EIA_API_KEY env var"
    
    series_id= "PET.EMM_EPMR_PTE_SNY_DPG.W"
    url= f"https://api.eia.gov/v2/seriesid/{series_id}?api_key={EIA_API_KEY}&length=1"
    print("[EIA URL]", url)
    
    rsp = requests.get(url, timeout= 15)

    if rsp.status_code !=200:
        return f"EIA error: HTTP {rsp.status_code}"
    
    try:
        payload = rsp.json()
    except Exception:
        return "EIA error: invalid JSON"
    
    try:
        row = payload["response"]["data"][0]
        period = row.get("period")
        value = row.get("value")
    except(KeyError,IndexError,TypeError):
        return "EIA error: missing data"
    
    if value is None or period is None:
        return "EIA error: incomplete data"
    try:
        price = float(value)
    except(ValueError, TypeError):
        return f"EIA error, bad value{value}"
    
    return(
        f"EIA NY Weekly regular gasoline: \n"
        f"Week ending {period}: ${price:.3f} per gallon"
    )


if __name__ == "__main__":
    print(get_eia_ny_weekly())


