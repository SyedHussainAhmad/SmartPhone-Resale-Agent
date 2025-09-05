from .state_schema import PricePredictionState
import pandas as pd

def preprocess_input_mobile(state: PricePredictionState) -> PricePredictionState:
    """Preprocesses input mobile and drops unnecessary features
    """
    input_data = state["input_mobile"]

    if input_data is None:
        raise ValueError("No input_mobile in state")

    input_dict = input_data.model_dump()

    # Clean RAM and Storage: remove 'GB'
    for field in ["ram", "storage"]:
        val = input_dict.get(field)
        if isinstance(val, str) and "GB" in val.upper():
            numeric_part = ''.join(filter(str.isdigit, val))
            input_dict[field] = int(numeric_part) if numeric_part else None

    # Convert bools to ints
    for key, value in input_dict.items():
        if isinstance(value, bool):
            input_dict[key] = int(value)

    df = pd.DataFrame([input_dict])

    # Drop unnecessary fields
    drop_cols = ["price", "images", "post_date", "listing_source", "city"]
    df.drop(columns=[col for col in drop_cols if col in df.columns], inplace=True)

    state["processed_input_df"] = df

    return state

