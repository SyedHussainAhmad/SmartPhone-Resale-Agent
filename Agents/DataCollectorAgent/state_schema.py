from typing import List, Optional, TypedDict, Dict
from .models import UsedMobile 

class DataCollectorState(TypedDict):
    model: Optional[str] = None
    raw_listings: Optional[List[Dict[str, str]]] = None
    structured_mobiles: Optional[List[UsedMobile]] = None
    saved: Optional[bool] = False
