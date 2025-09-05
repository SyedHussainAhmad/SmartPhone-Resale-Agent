from Agents.ImageUnderstandingAgent.graph import imageunderstand_app
from Agents.PricePredictionAgent.graph import pricepredictor_app
from Agents.SpecsFetcherAgent.graph import specsfetcher_app, SpecsFetcherState
from langchain_core.tools import Tool
from models import UsedMobile
from typing import Any
import json

# Tools wrappers

def parse_input(x):
    """ Handles __arg1 string case, direct string case, and ensures final output is a dict.
    """
    if isinstance(x, dict) and "__arg1" in x and isinstance(x["__arg1"], str):
        try:
            x = json.loads(x["__arg1"])
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in __arg1: {x['__arg1']}")
    elif isinstance(x, str):
        try:
            x = json.loads(x)
        except json.JSONDecodeError:
            x = {"model": x}
    if not isinstance(x, dict):
        raise ValueError(f"Expected dict, got {type(x)}")
    return x

def parse_input_image_tool(x):
    
    if isinstance(x, dict) and "__arg1" in x and isinstance(x["__arg1"], str):
        try:
            x = json.loads(x["__arg1"])
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in __arg1: {x['__arg1']}")
    elif isinstance(x, str):
        try:
            x = json.loads(x)
        except json.JSONDecodeError:
            x = {"image_path": x}
    if not isinstance(x, dict):
        raise ValueError(f"Expected dict, got {type(x)}")
    return x


def specs_fetcher_wrapper(x):
    x = parse_input(x)
    model = x.get("model") or x.get("model_name") or ""
    brand = x.get("brand") or x.get("brand_name") or ""
    if not model:
        raise ValueError("Model name is required.")
    return SpecsFetcherState(model_name=model, brand_name=brand)

def image_understanding_wrapper(x):

    x = parse_input_image_tool(x)

    print(f"[DEBUG] Parsed input: {x} (type: {type(x)})")

    if "image_path" not in x:
        raise ValueError(f"Input must contain 'image_path' key, got keys: {list(x.keys())}")

    image_path = x["image_path"]

    print("Image path: ", image_path)

    return imageunderstand_app.invoke({'image_path':image_path})



def convert_fields(data: dict[str, Any]) -> dict[str, Any]:
    if "condition" in data:
        try:
            data["condition"] = int(data["condition"])
        except:
            raise ValueError("Field 'condition' must be an integer (e.g., 9)")

    if "pta_approved" in data:
        if isinstance(data["pta_approved"], str):
            data["pta_approved"] = data["pta_approved"].lower() in ["true", "yes", "1"]

    for key in [
        "is_panel_changed", "screen_crack", "panel_dot", "panel_line", "panel_shade",
        "camera_lens_ok", "fingerprint_ok", "with_box", "with_charger"
    ]:
        if key in data:
            if isinstance(data[key], str):
                data[key] = data[key].lower() in ["true", "yes", "1"]

    return data

def price_prediction_wrapper(x):
    x = parse_input(x)

    if "input_mobile" not in x:
        raise ValueError("Missing required field: 'input_mobile'")

    x["input_mobile"] = convert_fields(x["input_mobile"])
    
    validated_mobile = UsedMobile(**x["input_mobile"])

    return pricepredictor_app.invoke({'input_mobile':validated_mobile})


# Tools

image_understanding_tool = Tool(
    name="ImageUnderstandingAgent",
    description="""
    Use this tool when the user uploads an image of a mobile's back and wants to identify the brand and model.
    
    CRITICAL INPUT FORMAT:
    - Input must be a JSON object with `image_path` key
    - Use forward slashes (/) in paths, never backslashes (\)
    - Example: {"image_path": "C:/Users/dell/AppData/Local/Temp/image.jpg"}
    - Do NOT use nested JSON strings or double escaping
    
    Output: Detected model and brand.
    """,
    func=lambda x: imageunderstand_app.invoke(image_understanding_wrapper(x))
)

price_prediction_tool = Tool(
    name="PricePredictionAgent",
    description="""
    Use this tool when the user wants to **predict the price** of a used mobile.

    Input should be a JSON object with a field `input_mobile` containing known details about the mobile phone.

    Required fields inside `input_mobile`:
    - model (e.g., "Hot 10")
    - condition (integer from 1 to 10)
    - pta_approved (true or false) ("cpid approved", "cpid", "pta" means its pta_approved = true )
      ("non pta", "sim lock", "jv" means its not approved i.e pta_approved = false)

    Optional fields that can also be provided (if known by user):
    - ram (e.g., "4GB")
    - storage (e.g., "64GB")
    - is_panel_changed, screen_crack, panel_dot, panel_line, panel_shade,
    - camera_lens_ok, fingerprint_ok,
    - with_box, with_charger

    Example:
    {
        "input_mobile": {
            "model": "Hot 10",
            "ram": "4GB",
            "storage": "64GB",
            "condition": 9,
            "pta_approved": true,
            "screen_crack": false,
            "with_charger": true
        }
    }

    The more complete the input, the more accurate the price prediction.

    Note:
    - If this tool returns need_fresh_data = True, it means we need fresh data to scrape from olx for that model. Then DataCollectorAgent should be used
    """,
    func=lambda x: price_prediction_wrapper(x)
)


specs_fetcher_tool = Tool(
    name="SpecsFetcherAgent",
    description="""
    Use this tool when the user wants to fetch specifications of a mobile model.
    Input: JSON with `model_name` (e.g. {"model_name": "Galaxy A52"})
    Input must be JSON like: {\"model_name\": \"Pixel 6a\"}"
    Output: Dictionary of specifications.
    """,
    func=lambda x: specsfetcher_app.invoke(specs_fetcher_wrapper(x))
)

tools = [
    image_understanding_tool,
    price_prediction_tool,
    specs_fetcher_tool
]