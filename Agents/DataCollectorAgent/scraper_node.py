import cloudscraper
from bs4 import BeautifulSoup
import requests
from time import sleep
import random
from .state_schema import DataCollectorState
import pandas as pd
from urllib.parse import quote_plus

scraper = cloudscraper.create_scraper()

BASE_URL = "https://www.olx.com.pk/mobile-phones_c1411"
HEADERS = {"User-Agent": "Mozilla/5.0"}
scraper = requests.Session()
scraper.headers.update(HEADERS)


def get_ads_from_page(page_num, model_query):
    encoded_query = quote_plus(model_query)
    url = f"https://www.olx.com.pk/mobile-phones_c1411/q-{encoded_query}/?page={page_num}"
    print(f"Scraping: {url}")
    
    res = scraper.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    ads = soup.select("li[aria-label='Listing']")
    listings = []

    for ad in ads:
        try:
            title_tag = ad.select_one("h2._1093b649")
            price_tag = ad.select_one("div[aria-label='Price'] span")
            location_tag = ad.select_one("span.f047db22")
            link_tag = ad.find("a", href=True)

            if not all([title_tag, price_tag, location_tag, link_tag]):
                continue

            title = title_tag.text.strip()
            price = price_tag.text.strip()
            location = location_tag.text.strip()
            link = "https://www.olx.com.pk" + link_tag["href"]

            ad_res = scraper.get(link)
            ad_soup = BeautifulSoup(ad_res.text, "html.parser")

            desc_tag = ad_soup.select_one("div[aria-label='Description'] div._7a99ad24 span")
            description = desc_tag.text.strip() if desc_tag else ""

            details = {}
            detail_tags = ad_soup.select("div[aria-label='Details'] div._0272c9dc.cd594ce1")
            for detail in detail_tags:
                spans = detail.find_all("span")
                if len(spans) == 2:
                    key = spans[0].text.strip()
                    value = spans[1].text.strip()
                    details[key] = value

            image_tags = ad_soup.select("div.image-gallery-slide img")
            image_urls = [img['src'] for img in image_tags if img.get('src')]

            listings.append({
                "title": str(title or ""),
                "price": str(price),
                "location": str(location or ""),
                "link": str(link or ""),
                "description": str(description or ""),
                "brand": str(details.get("Brand", "")),
                "model": str(details.get("Model", "")),
                "condition": str(details.get("Condition", "")),
                "images": ", ".join(map(str, image_urls or [])) 
            })

            sleep(random.uniform(1.5, 4))  # wait for crawling

        except Exception as e:
            print("Skipping ad due to error:", e)
            continue

    return listings



def scrape_data(state: DataCollectorState) -> DataCollectorState:
    """Scrape data from OLX based on the model specified in the state."""

    if not state['model']:
        print("No model specified. Exiting.")
        return state

    print(f"Collecting data for model: {state['model']}")

    all_listings = []

    try:
        page_num = 1
        while True:
            listings = get_ads_from_page(page_num, state['model'])
            if not listings:
                print(f"No listings found on page {page_num}. Stopping.")
                break

            all_listings.extend(listings)

            if len(all_listings) >= 100:
                print("Collected enough listings (100+). Stopping.")
                break

            page_num += 1
            sleep(random.uniform(3, 6))  # polite crawling

    except Exception as e:
        print(f"❌ Error while scraping data: {e}")

    df = pd.DataFrame(all_listings)
    df.to_csv("samsung_s22.csv", index=False, encoding="utf-8-sig")
    print(f"✅ Saved {len(df)} listings to samsung_s22.csv")

    state['raw_listings'] = all_listings
    print(f"✅ Collected {len(all_listings)} listings.")
    return state

