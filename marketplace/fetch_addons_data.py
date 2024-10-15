# fetch_addons_data.py
import json
from pathlib import Path
import sys

# Add the root directory to the Python path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from services.jira_service import JiraService
from utils.file_utils import write_json_to_file

class MarketplaceAddonFetcher:
    def __init__(self):
        self.jira_service = JiraService()

    def fetch_addons(self, application):
        addons = []
        route = f"rest/2/addons?filter=trending&limit=50&hosting=cloud&offset=0&application={application}"

        while route:
            print(route)
            response = self.jira_service.get_all_addons(route)
            if response and "_embedded" in response and "addons" in response["_embedded"]:
                addons.extend(response["_embedded"]["addons"])
                next_links = response["_links"].get("next", [])
                route = next_links[0]["href"] if next_links else None
            else:
                route = None

        return addons

    def save_addons_to_file(self, output_path):
        applications = ["jira", "confluence"]
        all_addons = []

        for application in applications:
            addons = self.fetch_addons(application)
            for addon in addons:
                all_addons.append({
                    "Name": addon.get("name"),
                    "Id": addon.get("id"),
                    "Link": f"{self.jira_service.marketplace_url}{addon['_links']['alternate']['href']}",
                    "Summary": addon.get("summary"),
                    "Tag Line": addon.get("tagLine"),
                    "Product Group": application,
                    "Categories": [cat.get("name") for cat in addon["_embedded"]["categories"]]
                })

        write_json_to_file(output_path, all_addons)
        print(f"Saved {len(all_addons)} addons to {output_path}")

if __name__ == "__main__":
    fetcher = MarketplaceAddonFetcher()
    output_path = Path(__file__).resolve().parent / "data" / "raw_addon_details.json"
    fetcher.save_addons_to_file(str(output_path))