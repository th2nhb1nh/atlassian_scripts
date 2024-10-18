import base64
import itertools
import re
import json
import requests

def encode_base64(string):
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')

def clean_string(string):
    return re.sub(r'[^a-zA-Z0-9]', ' ', string).upper()

def get_all_random_combinations(string, count, exclude_indices):
    available_chars = [char for i, char in enumerate(string) if i not in exclude_indices]
    return [''.join(comb) for comb in itertools.combinations(available_chars, count)]

def remove_short_combinations(combinations):
    return [comb for comb in combinations if len(comb) == 4]

def limit_potential_initials(potential_initials):
    return potential_initials[:15]

def handle_one_word(words, product_group):
    word = words[0]
    product_code = product_group[:2].upper()
    first_two, first_four = word[:2], word[:4]
    last_two, last_char = word[-2:], word[-1]
    random_combinations = get_all_random_combinations(word, 4, set())
    
    potential_initials = [
        first_two + product_code,
        first_two + last_two,
        word[0] + last_char + product_code,
        first_four
    ] + random_combinations
    
    potential_initials = remove_short_combinations(potential_initials)
    potential_initials = limit_potential_initials(potential_initials)
    all_initials = "LIC-C-" + "-A, LIC-C-".join(potential_initials) + "-A"
    return all_initials

def handle_two_words(words, product_group):
    product_code = product_group[:2].upper()
    first_two, first_four = words[0][:2], words[0][:4]
    initials = ''.join(word[0] for word in words)
    last_two = words[1][-2:]
    random_combinations = get_all_random_combinations(''.join(words), 2, {0, 1, len(words[0])})
    
    potential_initials = [
        first_two + product_code,
        first_four,
        initials + last_two,
        initials + product_code
    ] + [initials + comb for comb in random_combinations]
    
    potential_initials = remove_short_combinations(potential_initials)
    potential_initials = limit_potential_initials(potential_initials)
    all_initials = "LIC-C-" + "-A, LIC-C-".join(potential_initials) + "-A"
    return all_initials

def handle_three_words(words, product_group):
    product_code = product_group[:2].upper()
    initials = ''.join(word[0] for word in words)
    first_four = initials + words[2][1] if len(initials) == 3 else initials[:4]
    last_two, last_char = words[-1][-2:], words[-1][-1]
    random_combinations = get_all_random_combinations(''.join(words), 2, {0, 1, 2})
    
    potential_initials = [
        initials + last_char,
        first_four,
        initials[:2] + last_two,
        initials[:2] + product_code
    ] + [initials[:2] + comb for comb in random_combinations]
    
    potential_initials = remove_short_combinations(potential_initials)
    potential_initials = limit_potential_initials(potential_initials)
    all_initials = "LIC-C-" + "-A, LIC-C-".join(potential_initials) + "-A"
    return all_initials

def handle_four_or_more_words(words, product_group):
    product_code = product_group[:2].upper()
    initials = ''.join(word[0] for word in words)
    first_four = initials[:4]
    last_two = words[-1][-2:]
    random_combinations = get_all_random_combinations(''.join(words), 2, {0, 1, 2})
    
    potential_initials = [
        first_four,
        initials[:4],
        initials[:2] + last_two,
        initials[:2] + product_code
    ] + [initials[:2] + comb for comb in random_combinations]
    
    potential_initials = remove_short_combinations(potential_initials)
    potential_initials = limit_potential_initials(potential_initials)
    all_initials = "LIC-C-" + "-A, LIC-C-".join(potential_initials) + "-A"
    return all_initials

def get_initials(string, product_group):
    words = [word for word in clean_string(string).split() if word not in ['FOR', 'TO', 'AND', 'WITH', 'BY']]
    
    if len(words) == 1:
        return handle_one_word(words, product_group)
    elif len(words) == 2:
        return handle_two_words(words, product_group)
    elif len(words) == 3:
        return handle_three_words(words, product_group)
    else:
        return handle_four_or_more_words(words, product_group)

def send_to_zapier(payload, webhook_url):
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(webhook_url, data=payload, headers=headers)
        if response.status_code == 200:
            print("Successfully sent data to Zapier.")
        else:
            print(f"Failed to send data. Status Code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while sending data: {e}")

def main(input_data):
    item_code = get_initials(input_data['name'], input_data['product_group'])
    output_json = {
        "Name": input_data['name'],
        "Id": input_data['id'],
        "Add-on Key": input_data['key'],
        "Link": input_data['link'],
        "Summary": input_data['summary'],
        "Product Group": input_data['product_group'],
        "Item Code": item_code,
    }

    payload = json.dumps(output_json, indent=4)
    webhook_url = "https://automation.atlassian.com/pro/hooks/<webhook-id>"
    send_to_zapier(payload, webhook_url)

    return output_json

output = main(input_data)
print(output)