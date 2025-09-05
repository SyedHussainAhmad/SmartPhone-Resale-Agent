from pymongo import MongoClient
from datetime import datetime, timezone
from .state_schema import DataCollectorState
from bson import ObjectId

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "mobile_scraper"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
COLLECTION_NAME = "used_mobiles"

def save_node(state: DataCollectorState) -> DataCollectorState:
    """ Save structured mobile data to MongoDB.
    """
    if not state['structured_mobiles']:
        print("No structured mobile data to save.")
        return state

    print(f"Saving {len(state['structured_mobiles'])} records to DB...")

    collection = db[COLLECTION_NAME]

    new_entries = []
    now = datetime.now(timezone.utc)


    for mobile in state['structured_mobiles']:
        data = mobile.model_dump()
        data["extraction_date"] = now   # To keep fresh data 

        data["_id"] = ObjectId()  
        new_entries.append(data)

    if new_entries:
        collection.insert_many(new_entries)

    state['saved'] = True
    print("Data saved successfully.")
    return state

