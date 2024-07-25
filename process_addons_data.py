import json
import re
from collections import defaultdict
from utils.file_utils import write_json_to_file, read_json
from utils.string_handling import get_initials

class AddonCodeProcessor:
    def __init__(self):
        self.existing_codes = set()
        self.failed_addons = []

    def handle_addon_code(self, name, product_group):
        return get_initials(name, self.existing_codes, product_group)

    def categorize_addons(self, addons):
        categorized_addons = defaultdict(list)
        for addon in addons:
            words = len(re.findall(r"[\w']+", addon.get("Name", "")))
            categorized_addons[words].append(addon)
        return categorized_addons

    def parse_addon_details(self, categorized_addons):
        parsed_addons = []
        for category in sorted(categorized_addons.keys()):
            for addon in categorized_addons[category]:
                application = addon.get("Product Group", "")
                addon_name = addon.get("Name", "")
                product_code = self.handle_addon_code(addon_name, application)
                if not product_code:
                    self.failed_addons.append(addon)
                    continue
                parsed_addons.append({
                    "Name": addon.get("Name"),
                    "Id": addon.get("Id"),
                    "Summary": addon.get("Summary"),
                    "Tag Line": addon.get("Tag Line"),
                    "Product Group": addon.get("Product Group"),
                    "Item Code": f"LIC-C-{product_code}-A",
                    "Categories": addon.get("Categories", [])
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
                print(f"{code}: {names}")
        else:
            print("No duplicate product codes found.")

    def process_addons(self, input_file, file_prefix):
        addons = read_json(input_file)
        categorized_addons = self.categorize_addons(addons)
        parsed_addons = self.parse_addon_details(categorized_addons)
        self.check_duplicates(parsed_addons)

        total_count = len(parsed_addons)
        print(f"Success: All {total_count} addons have been processed and will be saved in multiple files.")

        # Break the output into new files per 100 records
        for i in range(0, total_count, 100):
            output_file = f"{file_prefix}_{i // 100 + 1}.json"
            write_json_to_file(output_file, parsed_addons[i:i + 100])
            print(f"Saved {len(parsed_addons[i:i + 100])} addons to {output_file}")

        # Save failed addons to a new file
        failed_output_file = "data/failed_addons.json"
        write_json_to_file(failed_output_file, self.failed_addons)
        print(f"Saved {len(self.failed_addons)} failed addons to {failed_output_file}")

if __name__ == "__main__":
    processor = AddonCodeProcessor()
    processor.process_addons("data/raw_addon_details.json", "data/addon_details")
