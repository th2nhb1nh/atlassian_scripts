# marketplace_get_all_addons.py
import json
from pathlib import Path
from services.jira_service import JiraService
from services.base_service import BaseService
from utils.file_utils import write_json_to_file
from utils.string_handling import get_initials

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

    def handle_addon_code(self, name):
        return get_initials(name)

    def parse_addon_details(self, addons, application):
        parsed_addons = []
        for addon in addons:
            product_code = self.handle_addon_code(addon.get("name", ""))
            parsed_addons.append({
                "Name": addon.get("name"),
                "Id": addon.get("id"),
                # "Key": addon.get("key"),
                "Summary": addon.get("summary"),
                "Tag Line": addon.get("tagLine"),
                "Product Group": application,
                "Item Code": f"LIC-C-{product_code}-A",
                "Categories": [cat.get("name") for cat in addon["_embedded"]["categories"]]
            })
        return parsed_addons

    def save_addons_to_files(self, file_prefix):
        applications = ["jira", "confluence"]
        all_addons = []

        for application in applications:
            addons = self.fetch_addons(application)
            parsed_addons = self.parse_addon_details(addons, application)
            all_addons.extend(parsed_addons)
            app_count = len(parsed_addons)
            print(f"Total fetched addons for {application}: {app_count}")

        total_count = len(all_addons)
        print(f"Success: All {total_count} addons have been fetched and will be saved in multiple files.")

        # Break the output into new files per 100 records
        for i in range(0, total_count, 100):
            output_file = f"{file_prefix}_{i // 100 + 1}.json"
            write_json_to_file(output_file, all_addons[i:i + 100])
            print(f"Saved {len(all_addons[i:i + 100])} addons to {output_file}")

if __name__ == "__main__":
    fetcher = MarketplaceAddonFetcher()
    fetcher.save_addons_to_files("data/addon_details")
