import re
import requests
from dotenv import load_dotenv
import os
from .state_schema import SpecsFetcherState

load_dotenv()

GCS_API_KEY = os.getenv("GCS_API_KEY")
GCX_CX = os.getenv("GCS_CX")

def search_gsmarena_url(state: SpecsFetcherState) -> SpecsFetcherState:
    api_key = GCS_API_KEY              
    cx = GCX_CX                 

    query = f"{state['model_name']} site:gsmarena.com"
    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": api_key,
        "cx": cx,
        "q": query
    }

    response = requests.get(url, params=params)
    print(response)  # Debug status code

    if response.status_code != 200:
        print("❌ API Error:", response.status_code)
        return state

    data = response.json()
    for item in data.get("items", []):
        href = item.get("link", "")
        print("link:", href)
        if "gsmarena.com" in href and re.search(r'-\d+\.php', href):
            state["gsmarena_url"] = href
            break

    return state