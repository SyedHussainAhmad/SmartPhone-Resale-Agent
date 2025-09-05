from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from .models import UsedMobile 
from dotenv import load_dotenv
from .state_schema import DataCollectorState
import time

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


prompt = ChatPromptTemplate.from_template("""
You are a smart assistant that extracts structured information from used mobile listings. You are given the following raw input fields scraped from OLX:

- Title: {title}
- Description: {description}
- Brand: {brand}
- Model: {model}
- Overall User Condition Note (free text): {condition}
- Price: {price}
- Location: {location}

Using this information, return a JSON object with the following fields:

- brand  
- model  
- ram  
- storage  
- condition (Rate out of 10 based on user's tone and overall language, e.g. "10/10", "good condition", etc. — ignore technical issues like fingerprint problems, panel cracks, etc.)  
- pta_approved  
- is_panel_changed  
- screen_crack  
- panel_dot  
- panel_line  
- panel_shade
- camera_lens_ok  
- fingerprint_ok  
- with_box  
- with_charger  
- price  
- city  
- listing_source (always "OLX")  
- images (list of URLs)  
- post_date

### Assumptions:
- If the listing **does not explicitly mention any problem** related to display, fingerprint, screen, or accessories, **assume everything is OK (i.e., set those fields accordingly):**
    - is_panel_changed → false  
    - screen_crack → false  
    - panel_dot → false  
    - panel_line → false
    - panel_shade → false
    - camera_lens_ok → true  
    - fingerprint_ok → true  
    - with_box → false  
    - with_charger → false

- If **PTA approval is not mentioned explicitly**, assume the device is **PTA approved**. However, set `pta_approved` to `false` if any of the following terms appear:  
    - "non PTA"  
    - "PTA not approved"  
    - "SIM lock"  
    - "JV phone"  

- Do not leave these assumption-based fields as null unless something directly contradicts the rule.

- Return `null` for any **other field** that cannot be confidently extracted from the input.

- Use only what's present in the input; **do not hallucinate or guess beyond the assumption rules.**

**Guidance for 'condition' field (out of 10):**

Lower the score (3–7) if the tone suggests:  
- "scratches", "scratchy", "visible marks"  
- "rough use", "daily used", "used for 2+ years"  
- "broken back", "dented", "chipped", "damaged"  
- "repaired"

Raise the score (8–10) if the tone includes:  
- "scratchless", "like new", "excellent condition"  
- "carefully used", "single hand used", "used with care"  
- "10/10", "almost new", "fresh condition", "mint"

Focus only on subjective tone and handling for the `condition` score. Ignore technical issues — they're handled separately.

Return the result strictly as a **JSON object**.
""")


chain = prompt | llm.with_structured_output(UsedMobile)


def extract_data_node(state: DataCollectorState) -> DataCollectorState:
    """ Extract structured data from raw listings in the state.
    """
    structured_data = []

    for listing in state['raw_listings']:
        try:
            mobile: UsedMobile = chain.invoke({
                "title": listing.get("title", ""),
                "description": listing.get("description", ""),
                "brand": listing.get("brand", ""),
                "model": listing.get("model", ""),
                "condition": listing.get("condition", ""),
                "price": listing.get("price", ""),
                "location": listing.get("location", "")
            })
            mobile.post_date = listing.get("post_date", "")
            mobile.images = listing.get("images","")
            structured_data.append(mobile)
            print(f"Mobile created: {mobile.model} - {len(structured_data)}")
            time.sleep(6)   # wait to not exceed gemini limit
        except Exception as e:
            print("❌ Extraction failed:", e)

    state['structured_mobiles'] = structured_data
    print(f"✅ Extracted {len(structured_data)} UsedMobile entries.")
    return state
