from langgraph.graph import StateGraph, END
from .state_schema import SpecsFetcherState
from .get_gsmarena_url import search_gsmarena_url
from .extract_specs import scrape_gsmarena_specs


graph = StateGraph(SpecsFetcherState)

graph.add_node("get_url", search_gsmarena_url)
graph.add_node("get_specs", scrape_gsmarena_specs)

graph.set_entry_point("get_url")
graph.add_edge("get_url", "get_specs")
graph.add_edge("get_specs", END)

specsfetcher_app = graph.compile()


