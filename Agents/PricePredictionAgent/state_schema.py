from typing import Optional, List, TypedDict
from .models import UsedMobile
import pandas as pd
from sklearn.base import RegressorMixin

class PricePredictionState(TypedDict):
    input_mobile: Optional[UsedMobile] = None
    raw_training_data: Optional[List[UsedMobile]] = None
    processed_training_df: Optional[pd.DataFrame] = None
    processed_input_df: Optional[pd.DataFrame] = None
    model: Optional[RegressorMixin] = None  # e.g., RandomForestRegressor
    predicted_price: Optional[float] = None
    need_fresh_data: Optional[bool] = None
