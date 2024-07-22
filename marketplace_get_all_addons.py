# marketplace_get_all_addons.py
import json
from pathlib import Path
from services.jira_service import JiraService
from utils.file_utils import write_json_to_file

class MarketplaceAddonFetcher:
    def __init__(self):
        self.jira_service = JiraService()

    def fetch_addons(self):
        addons = []
        route = "rest/2/addons?filter=trending&limit=50&hosting=cloud&offset=0"

        while route:
            response = self.jira_service.get_all_addons(route)
            if response and "_embedded" in response and "addons" in response["_embedded"]:
                addons.extend(response["_embedded"]["addons"])
                next_links = response["_links"].get("next", [])
                route = next_links[0]["href"] if next_links else None
            else:
                route = None

        return addons, len(addons)

    def save_addons_to_file(self, file_name):
        addons, total_count = self.fetch_addons()
        write_json_to_file(file_name, addons)

        print(f"Total fetched addons: {total_count}")
        if total_count == len(addons):
            print(f"Success: All {total_count} addons have been fetched and saved.")
        else:
            print(f"Warning: Expected {total_count} addons, but only {len(addons)} were fetched.")

if __name__ == "__main__":
    fetcher = MarketplaceAddonFetcher()
    output = Path("data/addons.json")
    fetcher.save_addons_to_file(output)
