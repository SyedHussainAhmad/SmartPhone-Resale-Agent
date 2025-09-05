from pymongo import MongoClient
from typing import List
from datetime import datetime, timedelta
from .state_schema import PricePredictionState
from .models import UsedMobile
from datetime import timezone
import re

client = MongoClient("mongodb://localhost:27017")
db = client["mobile_scraper"]
collection = db["used_mobiles"]

# how old data can be 
MAX_DATA_AGE_DAYS = 30

def fetch_training_data_node(state: PricePredictionState) -> PricePredictionState:
    input_mobile = state["input_mobile"]

    if input_mobile is None or input_mobile.model is None:
        raise ValueError("Input mobile or model not provided")

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=MAX_DATA_AGE_DAYS)

    cutoff_date_iso = cutoff_date.isoformat()

    query = {
        "model": {
            "$regex": re.escape(input_mobile.model),
            "$options": "i"
        }
    }

    result = collection.find(query)
    training_data: List[UsedMobile] = []
    latest_date = None
    fresh_data_count = 0

    for doc in result:
        try:
            if "images" in doc and isinstance(doc["images"], str):
                doc["images"] = [img.strip() for img in doc["images"].split(",") if img.strip()]

            if "extraction_date" in doc and isinstance(doc["extraction_date"], str):
                doc_date = datetime.fromisoformat(doc["extraction_date"])
                if not latest_date or doc_date > latest_date:
                    latest_date = doc_date
                    
                if doc_date >= cutoff_date:
                    fresh_data_count += 1

            training_data.append(UsedMobile(**doc))

        except Exception as e:
            print(f"Skipping invalid record: {e}")
            print(f"Problematic document ID: {doc.get('_id', 'unknown')}")

    # if we need fresh data
    need_fresh_data = True
    
    if training_data:
        need_fresh_data = False

    state["raw_training_data"] = training_data if training_data else None
    state["need_fresh_data"] = need_fresh_data
    
    print(f"Found {len(training_data)} training records")
    print(f"Fresh records: {fresh_data_count}")
    print(f"Latest date: {latest_date}")
    print(f"Need fresh data: {need_fresh_data}")

    return state