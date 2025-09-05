from .state_schema import PricePredictionState
import pandas as pd
import re

def preprocess_training_data(state: PricePredictionState) -> PricePredictionState:
    raw_data = state["raw_training_data"]

    if raw_data is None or len(raw_data) == 0:
        return state

    processed_rows = []

    fallback_ram = None
    fallback_storage = None

    for item in raw_data:
        row = item.model_dump()
        ram = row.get("ram")
        storage = row.get("storage")

        if ram and "GB" in ram.upper() and storage and "GB" in storage.upper():
            fallback_ram = ram
            fallback_storage = storage
            break

    if not fallback_ram or not fallback_storage:
        raise ValueError("No valid RAM and Storage fallback found")

    for item in raw_data:
        row = item.model_dump()

        if not row.get("ram"):
            row["ram"] = fallback_ram
        if not row.get("storage"):
            row["storage"] = fallback_storage
        
        # Clean RAM and Storage
        for field in ["ram", "storage"]:
            val = row.get(field)

            if isinstance(val, str):
                # Extract the first number from the string
                match = re.search(r'\d+', val)
                if match:
                    row[field] = int(match.group())
                else:
                    row[field] = 6
            elif not isinstance(val, int):
                row[field] = 6

        # Convert bools to ints
        for key, value in row.items():
            if isinstance(value, bool):
                row[key] = int(value)

        processed_rows.append(row)

    df = pd.DataFrame(processed_rows)

    # Drop irrelevant features 
    drop_cols = ["images", "post_date", "listing_source", "city", "model", "brand"]
    df.drop(columns=[col for col in drop_cols if col in df.columns], inplace=True)

    state["processed_training_df"] = df

    return state