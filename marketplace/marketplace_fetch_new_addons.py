# marketplace_fetch_new_addons.py
import base64
import itertools
import re
import json
from collections import defaultdict
from pathlib import Path
import sys

# Add the root directory to the Python path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from services.jira_service import JiraService
from utils.file_utils import write_json_to_file

# String handling functions
def encode_base64(string):
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')

def is_duplicate(initials, existing_codes):
    return initials in existing_codes

def get_all_random_combinations(string, count, exclude_indices):
    available_chars = [string[i] for i in range(len(string)) if i not in exclude_indices]
    return [''.join(comb) for comb in itertools.combinations(available_chars, count)]

def handle_one_word(words, product_group, existing_codes):
    initials = ''.join(word[0].upper() for word in words)
    product_code = product_group[:2].upper()
    first_two = words[0][:2]
    first_three = words[0][:3]
    first_four = words[0][:4]
    last_two = words[0][-2:]
    last_char = words[0][-1]
    potential_initials = [
        first_two + product_code,
        first_two + last_two,
        initials + last_char + product_code,
        first_four,
    ][:15]  # Limit to 15 potential initials

    all_initials = "LIC-C-" + "-A, LIC-C-".join(potential_initials) + "-A"
    print(all_initials)

    return all_initials

def handle_two_words(words, product_group, existing_codes):
    first_two = words[0][:2]
    first_four = words[0][:4]
    product_code = product_group[:2].upper()
    initials = ''.join(word[0].upper() for word in words)
    last_two = words[1][-2:]
    random_combinations = get_all_random_combinations(''.join(words), 2, {0, 1, len(words[0])})
    potential_initials = (
        [
            first_two + product_code,
            first_four,
            initials[0] + initials[1] + last_two,
            initials[0] + initials[1] + product_code
        ] + [initials[0] + initials[1] + comb for comb in random_combinations]
    )[:15]  # Limit to 15 potential initials

    all_initials = "LIC-C-" + "-A, LIC-C-".join(potential_initials) + "-A"
    print(all_initials)

    return all_initials

def handle_three_words(words, product_group, existing_codes):
    initials = ''.join(word[0].upper() for word in words)
    first_four = ''.join(word[0].upper() for word in words[:4])
    product_code = product_group[:2].upper()
    last_two = words[-1][-2:]
    last_char = words[-1][-1]
    random_combinations = get_all_random_combinations(''.join(words), 2, {0, 1, 2})
    potential_initials = (
        [
            initials + last_char,
            first_four,
            initials[0] + initials[1] + last_two,
            initials[0] + initials[1] + product_code
        ] + [initials[0] + initials[1] + comb for comb in random_combinations]
    )[:15]  # Limit to 15 potential initials

    all_initials = "LIC-C-" + "-A, LIC-C-".join(potential_initials) + "-A"
    print(all_initials)

    return all_initials

def handle_four_or_more_words(words, product_group, existing_codes):
    initials = ''.join(word[0].upper() for word in words)
    first_three = ''.join(word[0].upper() for word in words[:3])
    first_four = ''.join(word[0].upper() for word in words[:4])
    product_code = product_group[:2].upper()
    last_two = words[-1][-2:]
    last_char = words[-1][-1]
    random_combinations = get_all_random_combinations(''.join(words), 2, {0, 1, 2})
    potential_initials = (
        [
            first_four,
            initials[0] + initials[1] + initials[2] + initials[3],
            initials[0] + initials[1] + last_two,
            initials[0] + initials[1] + product_code
        ] + [initials[0] + initials[1] + comb for comb in random_combinations]
    )[:15]  # Limit to 15 potential initials

    all_initials = "LIC-C-" + "-A, LIC-C-".join(potential_initials) + "-A"
    print(all_initials)

    return all_initials

def get_initials(string, existing_codes, product_group):
    words = re.findall(r"[\w']+", string.upper())
    words = [word for word in words if word not in ['FOR', 'TO', 'AND', 'WITH', 'BY']]

    if len(words) == 1:
        initials = handle_one_word(words, product_group, existing_codes)
    elif len(words) == 2:
        initials = handle_two_words(words, product_group, existing_codes)
    elif len(words) == 3:
        initials = handle_three_words(words, product_group, existing_codes)
    else:
        initials = handle_four_or_more_words(words, product_group, existing_codes)
    
    if initials and not is_duplicate(initials, existing_codes):
        existing_codes.add(initials)
        print(f"Addon: {words} with item code: {initials}")
        return initials.upper()
    else:
        print(f"Could not generate unique initials for: {words}")
        return None

# Marketplace Addon Fetching and Processing
class MarketplaceAddonFetcher:
    def __init__(self):
        self.jira_service = JiraService()
        self.existing_codes = set()
        self.failed_addons = []

    def fetch_addons(self, application):
        addons = []
        route = f"rest/2/addons?filter=new&limit=50&hosting=cloud&includeHidden=visibleInApp&includePrivate=false&offset=0&application={application}"

        print(route)
        response = self.jira_service.get_all_addons(route)
        if response and "_embedded" in response and "addons" in response["_embedded"]:
            addons.extend(response["_embedded"]["addons"])
            next_links = response["_links"].get("next", [])
            route = next_links[0]["href"] if next_links else None

        return addons

    def handle_addon_code(self, name, product_group):
        return get_initials(name, self.existing_codes, product_group)

    def parse_addon_details(self, addons, application):
        parsed_addons = []
        for addon in addons:
            product_code = self.handle_addon_code(addon.get("name", ""), application)
            parsed_addons.append({
                "Name": addon.get("name"),
                "Id": addon.get("id"),
                "Link": f"{self.jira_service.marketplace_url}{addon['_links']['alternate']['href']}",
                "Summary": addon.get("summary"),
                "Tag Line": addon.get("tagLine"),
                "Product Group": application,
                "Item Code": product_code,  # Directly using the formatted string from get_initials
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

    def save_addons_to_files(self, output_dir):
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
        output_file = output_dir / "addon_details.json"
        write_json_to_file(str(output_file), all_addons)
        print(f"Saved {total_count} addons to {output_file}")

        failed_output_file = output_dir / "failed_addons.json"
        write_json_to_file(str(failed_output_file), self.failed_addons)
        print(f"Saved {len(self.failed_addons)} failed addons to {failed_output_file}")

if __name__ == "__main__":
    fetcher = MarketplaceAddonFetcher()
    output_dir = Path(__file__).resolve().parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    fetcher.save_addons_to_files(output_dir)