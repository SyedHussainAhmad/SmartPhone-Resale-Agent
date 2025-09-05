from langgraph.graph import StateGraph, END
from .state_schema import DataCollectorState
from .scraper_node import scrape_data
from .extractor_node import extract_data_node
from .save_data_node import save_node


graph = StateGraph(DataCollectorState)

graph.add_node("scrape_data", scrape_data)
graph.add_node("extract_data", extract_data_node)
graph.add_node("save_data", save_node)

graph.set_entry_point("scrape_data")

graph.add_edge("scrape_data", "extract_data")
graph.add_edge("extract_data", "save_data")
graph.add_edge("save_data", END)

datacollector_app = graph.compile()


