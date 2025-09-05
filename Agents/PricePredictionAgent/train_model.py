from sklearn.ensemble import RandomForestRegressor
from .state_schema import PricePredictionState

def train_model_node(state: PricePredictionState) -> PricePredictionState:

    df = state["processed_training_df"]

    if df is None or "price" not in df.columns:
        raise ValueError("Training data missing or 'price' column not found.")

    # Drop rows with missing target
    df = df.dropna(subset=["price"])

    # Separate features and target
    X = df.drop(columns=["price"])
    y = df["price"]

    X, y = X.align(y, join="inner", axis=0)

    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    state["model"] = model

    return state
