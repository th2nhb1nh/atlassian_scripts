# marketplace_get_all_addons.py
import csv
import re
from collections import defaultdict
from services.jira_service import JiraService
from utils.file_utils import write_csv_to_file, read_csv
from utils.string_handling import get_initials

class MarketplaceAddonFetcher:
    def __init__(self):
        self.jira_service = JiraService()
        self.existing_codes = set()
        self.existing_addon_keys = set()
        self.failed_addons = []
        self.duplicate_addons = []

    def load_existing_data(self, csv_file):
        existing_addons = read_csv(csv_file)
        self.existing_codes = {addon['Item Code'] for addon in existing_addons}
        self.existing_addon_keys = {addon['Addon Key'] for addon in existing_addons}
        print(f"[INFO] Loaded {len(self.existing_codes)} existing codes and {len(self.existing_addon_keys)} existing addon keys from {csv_file}")

    def fetch_addons(self, application):
        addons = []
        route = f"rest/2/addons?filter=trending&limit=50&hosting=cloud&offset=0&application={application}"

        while route:
            print(f"[INFO] Fetching: {route}")
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

    def truncate_client_name(self, name):
        if len(name) <= 47:
            return name
        truncated = name[:47]
        if truncated[-1] == ' ':
            truncated = truncated[:46]
        return truncated + "..."

    def parse_addon_details(self, addons, application):
        parsed_addons = []
        sorted_addons = sorted(addons, key=lambda x: len(x.get("name", "")))
        
        for addon in sorted_addons:
            addon_key = addon.get("key")
            parsed_addon = {
                "Name": addon.get("name"),
                "Client Name": self.truncate_client_name(addon.get("name")),
                "Addon ID": addon.get("id"),
                "Addon Key": addon_key,
                "Summary": addon.get("summary"),
                "Product Group": application,
                "Link": f"{self.jira_service.marketplace_url}{addon['_links']['alternate']['href']}"
            }

            if addon_key in self.existing_addon_keys:
                self.duplicate_addons.append(parsed_addon)
                continue

            product_code = self.handle_addon_code(addon.get("name", ""), application)
            if not product_code:
                self.failed_addons.append(parsed_addon)
                continue
            
            parsed_addon["Item Code"] = f"LIC-C-{product_code}-A"
            parsed_addons.append(parsed_addon)

        return parsed_addons

    def save_addons_to_csv(self, file_prefix, csv_file):
        applications = ["jira", "confluence", "bitbucket", "compass"]
        all_addons = []

        self.load_existing_data(csv_file)

        for application in applications:
            addons = self.fetch_addons(application)
            parsed_addons = self.parse_addon_details(addons, application)
            all_addons.extend(parsed_addons)
            app_count = len(parsed_addons)
            print(f"[INFO] Total fetched addons for {application}: {app_count}\n")

        total_count = len(all_addons)
        print(f"[SUCCESS] All {total_count} addons have been fetched and will be saved in a CSV file.")

        fieldnames = ["Name", "Client Name", "Addon ID", "Addon Key", "Summary", "Product Group", "Item Code", "Link"]

        output_file = f"{file_prefix}.csv"
        write_csv_to_file(output_file, all_addons, fieldnames)
        print(f"[SUCCESS] Saved {total_count} addons to {output_file}")

        if self.failed_addons:
            failed_output_file = "data/failed_addons.csv"
            write_csv_to_file(failed_output_file, self.failed_addons, fieldnames)
            print(f"[WARNING] Saved {len(self.failed_addons)} failed addons to {failed_output_file}")
        else:
            print("[INFO] No failed addons to save.")

        if self.duplicate_addons:
            duplicate_output_file = "data/duplicate_addons.csv"
            write_csv_to_file(duplicate_output_file, self.duplicate_addons, fieldnames)
            print(f"[INFO] Saved {len(self.duplicate_addons)} duplicate addons to {duplicate_output_file}")
        else:
            print("[INFO] No duplicate addons to save.")

        print("\n[SUMMARY]")
        print(f"Total addons processed: {total_count + len(self.failed_addons) + len(self.duplicate_addons)}")
        print(f"New addons saved: {total_count}")
        print(f"Failed addons: {len(self.failed_addons)}")
        print(f"Duplicate addons: {len(self.duplicate_addons)}")

if __name__ == "__main__":
    fetcher = MarketplaceAddonFetcher()
    fetcher.save_addons_to_csv("data/addon_details", "158Addons.csv")