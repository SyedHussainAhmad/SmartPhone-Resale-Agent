**SmartPhone Resale Agent** is an intelligent, multi-agent system built with **LangGraph** that predicts the resale price of used mobile phones, identifies mobile models from images, and fetches detailed specifications.  
The system integrates web scraping, ML modeling, and multiple specialized agents to deliver accurate and up-to-date results.


https://github.com/user-attachments/assets/cb68fc59-0ea7-47d7-b86e-bd4684116593

---

## Features

- **🔍 Image-based Mobile Identification**
  - Detects **brand and model** from the back-side image of a mobile using **Bing Image Search API (RapidAPI)**.

- **📋 Mobile Specifications Lookup**
  - Fetches **detailed specifications** from **GSMArena** using Google Custom Search (GCS) and scraping.

- **💰 Used Mobile Price Prediction**
  - Predicts resale price using **RandomForestRegressor** trained on real OLX listings.
  - Takes into account **RAM, storage, and condition** (e.g., panel damage, accessories).

- **🔄 Data Refresh**
  - If data is missing or outdated (older than 1 month), the **PricePredictionAgent** triggers **DataCollectorAgent** to:
    - Scrape **fresh OLX listings**
    - Store them in **MongoDB**
    - Retrain the ML model and retry prediction

- **🧠 ReAct Supervisor Agent**
  - A **LangGraph ReAct-style agent** acts as the supervisor, deciding which sub-agent to call:
    - `PricePredictionAgent`
    - `SpecsFetcherAgent`
    - `ImageUnderstandingAgent`
  - `DataCollectorAgent` is used internally by `PricePredictionAgent` for data freshness.

- **💬 Natural Language Interaction**
  - Users can interact with the system in plain text:
    - *"Predict the price of this mobile"*
    - *"What model is this?"* (upload image)
    - *"Show me specifications of Infinix Hot 10"*

---

## 📊 Price Prediction Model
 - The price prediction model uses RandomForestRegressor.
 - It is trained on real OLX data stored in MongoDB.
 - Preprocessing steps:
    - Extracts numeric values from RAM/Storage strings (e.g., "4GB" → 4)
    - Converts all boolean fields (like panel_broken, with_box) to integers (0 or 1)
    - Drops irrelevant columns: images, post_date, listing_source, city, model, brand

---

## 🧩 System Architecture

```
User Query
│
▼
SupervisorAgent (LangGraph ReAct)
├── PricePredictionAgent ──> (DataCollectorAgent if needed)
├── SpecsFetcherAgent
└── ImageUnderstandingAgent
```

### 👤 Supervisor Agent
- Built with `LangGraph.create_react_agent`
- Handles natural queries and delegates to tools intelligently


### 🛠️ Subagents

| Agent | Role |
|-------|------|
| **ImageUnderstandingAgent** | Identifies mobile model from back image |
| **SpecsFetcherAgent**       | Gets full specs from GSMArena           |
| **PricePredictionAgent**    | Trains and predicts resale price        |
| **DataCollectorAgent**      | Scrapes listings from OLX and saves to DB (called internally by PricePredictionAgent if needed) |

---

## 🛠️ Tech Stack

| Component                 | Technology Used                              |
|---------------------------|----------------------------------------------|
| **Agents & Orchestration**| LangGraph ReAct, LangChain                   |
| **Scraping**              | OLX custom scraper, GSMArena scraping        |
| **Database**              | Local MongoDB                                |
| **Image Search**          | Bing Image Search API (RapidAPI), IMGBB API  |
| **ML Model**              | RandomForestRegressor (scikit-learn)         |
| **Search Engine**         | Google Custom Search (GCS) for GSMArena links|
| **Frontend (Optional)**   | Streamlit (for UI and visualization)         |

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/FassihShah/mobile-mas.git
cd mobile-mas
```
### 2. Create and Activate Virtual Environment
```
python -m venv venv
source venv\Scripts\activate
```
### 3. Install Dependencies
```
pip install -r requirements.txt
```
### 4. Create Environment variables
```
RAPIDAPI_KEY=your_rapidapi_key
IMGBB_API_KEY=your_api_key
BING_END_POINT=https://api.bing.microsoft.com/v7.0/images/search
GCS_API_KEY=your_google_custom_search_key
GCS_CX=your_custom_search_engine_id
```
### 5. Run the app
```
streamlit run app.py
```

## 👤 Author

**Syed Hussain Ahmad**  
- GitHub: [@SyedHussainAhmad](https://github.com/SyedHussainAhmad)  
- LinkedIn: [Syed Hussain Ahmad](https://www.linkedin.com/in/syedhussainahmad/)

---
⭐ Star this repository if you found it helpful!







