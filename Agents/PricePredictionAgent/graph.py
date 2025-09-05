from langgraph.graph import StateGraph, END
from .state_schema import PricePredictionState
from .fetch_training_data import fetch_training_data_node
from .preprocess_training_data import preprocess_training_data
from .preprocess_test_data import preprocess_input_mobile
from .train_model import train_model_node
from .predict_price import predict_price_node
from ..DataCollectorAgent.graph import datacollector_app
from .models import UsedMobile

# Node: Call datacollector if needed
def datacollector_call(state: PricePredictionState) -> PricePredictionState:
    model = state.get("input_mobile").model
    result = datacollector_app.invoke({"model": model})
    try:
        if result.get("saved") == True:
            state["need_fresh_data"] = False

    except Exception as e:
        print("Error while calling DataCollectorAgent:", e)

    return state

# ROUTE after fetch_training_data
def route1(state: PricePredictionState) -> str:
    if state.get("need_fresh_data") == True:
        return "datacollector_call"
    return "preprocess_training_data"

# ROUTE after datacollector_call
def route2(state: PricePredictionState) -> str:
    if state.get("need_fresh_data") == True:
        return END
    return "fetch_training_data"


graph = StateGraph(PricePredictionState)

graph.add_node("fetch_training_data", fetch_training_data_node)
graph.add_node("datacollector_call", datacollector_call)
graph.add_node("preprocess_training_data", preprocess_training_data)
graph.add_node("preprocess_input", preprocess_input_mobile)
graph.add_node("train_model", train_model_node)
graph.add_node("predict_price", predict_price_node)

graph.set_entry_point("fetch_training_data")
graph.add_conditional_edges(
    "fetch_training_data",
    route1,
    {
        "datacollector_call": "datacollector_call",
        "preprocess_training_data": "preprocess_training_data"
    }
)
graph.add_conditional_edges(
    "datacollector_call",
    route2,
    {
        "fetch_training_data": "fetch_training_data",
        END: END
    }
)
graph.add_edge("preprocess_training_data", "preprocess_input")
graph.add_edge("preprocess_input", "train_model")
graph.add_edge("train_model", "predict_price")
graph.add_edge("predict_price", END)
pricepredictor_app = graph.compile()

## Test
# input_mobile = UsedMobile(
#         brand="Samsung",
#         model="A52",
#         ram="4GB",
#         storage="128GB",
#         condition=9,
#         pta_approved=True,
#         is_panel_changed=False,
#         screen_crack=False,
#         panel_dot=True,
#         panel_line=False,
#         panel_shade=False,
#         camera_lens_ok=True,
#         fingerprint_ok=True,
#         with_box=False,
#         with_charger=False,
#         price=None,
#         city="Lahore",
#         listing_source="OLX",
#         images=[],
#         post_date=None
#     )


# initial_state = PricePredictionState(input_mobile=input_mobile)

