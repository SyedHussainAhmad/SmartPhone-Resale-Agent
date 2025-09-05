from typing import Optional, TypedDict
from .models import NewMobile

class SpecsFetcherState(TypedDict):
    model_name: Optional[str] = None
    brand_name: Optional[str] = None
    gsmarena_url: Optional[str] = None
    specs: Optional[NewMobile] = None
