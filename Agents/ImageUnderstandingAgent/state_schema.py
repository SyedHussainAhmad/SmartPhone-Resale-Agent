from typing import Optional, TypedDict

class ImageUnderstandingState(TypedDict):
    image_path: Optional[str] = None
    search_results: Optional[dict] = None
    model_name: Optional[str] = None
    brand_name: Optional[str] = None
