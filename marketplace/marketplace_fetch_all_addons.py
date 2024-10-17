# marketplace_get_all_addons.py
import json
import re
from collections import defaultdict
from pathlib import Path
import sys

# Add the root directory to the Python path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from services.jira_service import JiraService
from utils.file_utils import write_json_to_file, read_json
from utils.string_handling import get_initials

class MarketplaceAddonFetcher:
    def __init__(self):
        self.jira_service = JiraService()
        self.existing_codes = set()
        self.failed_addons = []

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

    def handle_addon_code(self, name, product_group):
        return get_initials(name, self.existing_codes, product_group)

    def parse_addon_details(self, addons, application):
        parsed_addons = []
        for addon in addons:
            product_code = self.handle_addon_code(addon.get("name", ""), application)
            if not product_code:
                self.failed_addons.append({
                    "Name": addon.get("name"),
                    "Add-on Key": addon.get("key"),
                    "Id": addon.get("id"),
                    "Link": f"{self.jira_service.marketplace_url}{addon['_links']['alternate']['href']}",
                    "Summary": addon.get("summary"),
                    "Tag Line": addon.get("tagLine"),
                    "Product Group": application,
                    "Categories": [cat.get("name") for cat in addon["_embedded"]["categories"]]
                })
                continue
            parsed_addons.append({
                "Name": addon.get("name"),
                "Add-on Key": addon.get("key"),
                "Id": addon.get("id"),
                "Link": f"{self.jira_service.marketplace_url}{addon['_links']['alternate']['href']}",
                "Summary": addon.get("summary"),
                "Tag Line": addon.get("tagLine"),
                "Product Group": application,
                "Item Code": f"LIC-C-{product_code}-A",
                "Categories": [cat.get("name") for cat in addon["_embedded"]["categories"]]
            })
        return parsed_addons

    def check_duplicates(self, addons):
        code_count = defaultdict(list)
        for addon in addons:
            code_count[addon["Item Code"]].append(addon["Name"])
        
        duplicates = {code: names for code, names in code_count.items() if len(names) > 1}
        if duplicates:
            print("Found duplicate product codes:")
            for code, names in duplicates.items():
                print(f"Code: {code} is used by: {names}")
        else:
            print("No duplicate product codes found.")

    def save_addons_to_files(self, file_prefix, chunk_size):
        applications = ["jira", "confluence"]
        all_addons = []

        for application in applications:
            addons = self.fetch_addons(application)
            parsed_addons = self.parse_addon_details(addons, application)
            all_addons.extend(parsed_addons)
            app_count = len(parsed_addons)
            print(f"Total fetched addons for {application}: {app_count}")

        self.check_duplicates(all_addons)

        total_count = len(all_addons)
        print(f"Success: All {total_count} addons have been fetched and will be saved in multiple files.")

        # Break the output into new files per chunk_size records
        for i in range(0, total_count, chunk_size):
            output_file = output_dir / f"addon_details_{i // chunk_size + 1}.json"
            write_json_to_file(str(output_file), all_addons[i:i + chunk_size])
            print(f"Saved {len(all_addons[i:i + chunk_size])} addons to {output_file}")

        # Save failed addons to a new file
        failed_output_file = output_dir / "failed_addons.json"
        write_json_to_file(str(failed_output_file), self.failed_addons)
        print(f"Saved {len(self.failed_addons)} failed addons to {failed_output_file}")

if __name__ == "__main__":
    fetcher = MarketplaceAddonFetcher()
    output_dir = Path(__file__).resolve().parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    fetcher.save_addons_to_files(output_dir, chunk_size=100)