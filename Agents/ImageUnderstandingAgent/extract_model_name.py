from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from dotenv import load_dotenv
from .state_schema import ImageUnderstandingState

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

class ModelBrandOutput(BaseModel):
    brand_name: str
    model_name: str

BRANDS = [
    "Samsung", "Apple", "Xiaomi", "Oppo", "Vivo", "Realme", "Infinix",
    "OnePlus", "Huawei", "Tecno", "Nokia", "Sony", "LG", "Google",
    "Motorola", "Lenovo", "Asus", "Honor", "Vgo Tel", "Itel"
]


chain = llm.with_structured_output(ModelBrandOutput)

def extract_model_brand(state: ImageUnderstandingState) -> ImageUnderstandingState:
    raw_results = state.get("search_results")

    if not raw_results:
        raise ValueError("Missing search_results")

    # Extract useful text only
    results = []
    for item in raw_results.get("data", []):
        results.append({
            "title": item.get("title", ""),
            "image_url": item.get("image_url", "")
        })


    text_snippets = "\n".join(f"- {item['title']}" for item in results if item['title'])

    prompt = f"""
You are an expert in identifying smartphone models and brands.

From the text below, extract:
- The **brand name** (must be exactly one of: {', '.join(BRANDS)})
- The **most complete and accurate model name** (e.g., "Google Pixel 6a")

Instructions:
- Only use titles that clearly refer to a smartphone.
- Ignore irrelevant articles like updates, opinions, or general tech news.
- Do **not** make up or guess the model name. Only extract model names **that are clearly mentioned** in the titles or snippets.
- If multiple model names are mentioned, choose the **most frequently occurring one**.
- Be precise — prefer full model names over partial ones.

Text snippets:
{text_snippets}
"""

    result = chain.invoke(prompt)

    state["brand_name"] = result.brand_name
    state["model_name"] = result.model_name

    return state
