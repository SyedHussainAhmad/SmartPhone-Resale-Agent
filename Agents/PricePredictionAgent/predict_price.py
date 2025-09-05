from typing import cast
from .state_schema import PricePredictionState


def predict_price_node(state: PricePredictionState) -> PricePredictionState:
    if state["model"] is None or state["processed_input_df"] is None or state["input_mobile"] is None:
        raise ValueError("Model, processed input, or input_mobile is missing in state")

    model = state["model"]
    df = state["processed_input_df"].copy()

    drop_cols = ["model", "brand"]
    df.drop(columns=[col for col in drop_cols if col in df.columns], inplace=True)

    predicted_price = model.predict(df)[0]

    mobile = state["input_mobile"]

    if mobile.is_panel_changed:
        predicted_price *= 0.8

    if mobile.panel_dot:
        predicted_price *= 0.75

    if mobile.panel_line:
        predicted_price *= 0.7

    if mobile.panel_shade:
        predicted_price *= 0.75

    if mobile.screen_crack:
        predicted_price *= 0.7

    if mobile.camera_lens_ok is False:
        predicted_price *= 0.9

    if mobile.fingerprint_ok is False:
        predicted_price *= 0.85

    if mobile.pta_approved is False:
        predicted_price *= 0.8

    # Round to nearest 500
    predicted_price = round(predicted_price / 500) * 500

    state["predicted_price"] = predicted_price
    return state