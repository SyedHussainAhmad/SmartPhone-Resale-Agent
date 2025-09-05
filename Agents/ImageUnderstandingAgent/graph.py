from langgraph.graph import StateGraph, END
from .state_schema import ImageUnderstandingState
from .extract_model_name import extract_model_brand
from .search_by_image import search_by_image


graph = StateGraph(ImageUnderstandingState)

graph.add_node("upload_and_search", search_by_image)
graph.add_node("extract_model_brand", extract_model_brand)

graph.set_entry_point("upload_and_search")
graph.add_edge("upload_and_search", "extract_model_brand")
graph.add_edge("extract_model_brand", END)


imageunderstand_app = graph.compile()
