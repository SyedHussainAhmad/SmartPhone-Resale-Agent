from bs4 import BeautifulSoup
import requests
from typing import Optional
from .state_schema import SpecsFetcherState, NewMobile
import re


def convert_specs_to_mobile(specs: dict) -> NewMobile:
    def get(*keys: str) -> Optional[str]:
        for key in keys:
            if key in specs:
                return specs[key]
        return None

    def extract_year_from_release(release_info: Optional[str]) -> Optional[int]:
        if release_info:
            for token in release_info.split():
                if token.isdigit() and len(token) == 4:
                    return int(token)
        return None

    def parse_ram_and_storage(mixed_string):
        ram_set = set()
        storage_set = set()

        matches = re.findall(r'(\d+GB)\s+(\d+GB)\s+RAM', mixed_string)

        for storage, ram in matches:
            storage_set.add(storage)
            ram_set.add(ram)

        return sorted(storage_set), sorted(ram_set)

    mobile = NewMobile(
        brand=None,
        model=None,
        os=get("Platform - OS"),
        release_year=extract_year_from_release(get("Launch - Announced")),
        screen_size=get("Display - Size"),
        screen_resolution=get("Display - Resolution"),
        battery_capacity=get("Battery - Type"),
        main_camera=get(
            "Main Camera - Single",
            "Main Camera - Dual",
            "Main Camera - Triple",
            "Main Camera - Quad"
        ),
        selfie_camera=get(
            "Selfie camera - Single",
            "Selfie camera - Dual"
        ),
        chipset=get("Platform - Chipset"),
        cpu=get("Platform - CPU"),
        gpu=get("Platform - GPU"),
        network=get("Network - Technology"),
        network_bands=get("Network - 2G bands"),
        sim=get("Network - SIM"),
        weight=get("Body - Weight"),
        dimensions=get("Body - Dimensions"),
        usb=get("Comms - USB"),
        sensors=get("Features - Sensors"),
        price=get("Misc - Price")
    )

    if "Memory - Internal" in specs:
        storage_ram_str = specs["Memory - Internal"]
        storage_list, ram_list = parse_ram_and_storage(storage_ram_str)
        mobile.storage = ", ".join(storage_list)
        mobile.ram = ", ".join(ram_list)

    return mobile




def scrape_gsmarena_specs(state: SpecsFetcherState) -> SpecsFetcherState:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(state["gsmarena_url"], headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    specs = {}
    specs_list = soup.find("div", id="specs-list")
    current_section = None

    if specs_list:
        for row in specs_list.select("tr"):
            # New section title (rowspan)
            th = row.find("th", {"scope": "row"})
            if th:
                current_section = th.text.strip()

            # Extract key and value
            key_td = row.find("td", class_="ttl")
            value_td = row.find("td", class_="nfo")

            if key_td and value_td and current_section:
                key = key_td.text.strip()
                value = value_td.text.strip()
                specs[f"{current_section} - {key}"] = value

    state["specs"] = convert_specs_to_mobile(specs)
    state["specs"].model = state["model_name"]

    return state

