# string_handling.py
import base64
import itertools
import random
import re

def encode_base64(string):
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')

def is_duplicate(initials, existing_codes):
    return initials in existing_codes

def clean_string(string):
    cleaned = re.sub(r'[^a-zA-Z0-9]', ' ', string)
    return cleaned.upper()

def get_all_random_combinations(string, count, exclude_indices):
    available_chars = [string[i] for i in range(len(string)) if i not in exclude_indices]
    return [''.join(comb) for comb in itertools.combinations(available_chars, count)]

def remove_short_combinations(combinations):
    return [comb for comb in combinations if len(comb) == 4]

def handle_one_word(words, product_group, existing_codes):
    initials = ''.join(word[0].upper() for word in words)
    product_code = product_group[:2].upper()
    first_two = words[0][:2]
    first_three = words[0][:3]
    first_four = words[0][:4]
    last_two = words[0][-2:]
    last_char = words[0][-1]
    random_combinations = get_all_random_combinations(words[0], 4, set())
    potential_initials = [
        first_two + product_code,
        first_two + last_two,
        initials + last_char + product_code,
        first_four,
    ] + random_combinations
    potential_initials = remove_short_combinations(potential_initials)
    return potential_initials

def handle_two_words(words, product_group, existing_codes):
    first_two = words[0][:2]
    first_four = words[0][:4]
    product_code = product_group[:2].upper()
    initials = ''.join(word[0].upper() for word in words)
    last_two = words[1][-2:]
    random_combinations = get_all_random_combinations(''.join(words), 2, {0, 1, len(words[0])})
    potential_initials = [
        first_two + product_code,
        first_four,
        initials[0] + initials[1] + last_two,
        initials[0] + initials[1] + product_code
    ] + [initials[0] + initials[1] + comb for comb in random_combinations]
    potential_initials = remove_short_combinations(potential_initials)
    return potential_initials

def handle_three_words(words, product_group, existing_codes):
    initials = ''.join(word[0].upper() for word in words)
    first_four = ''.join(word[0].upper() for word in words[:4])
    product_code = product_group[:2].upper()
    last_two = words[-1][-2:]
    last_char = words[-1][-1]
    random_combinations = get_all_random_combinations(''.join(words), 2, {0, 1, 2})
    potential_initials = [
        initials + last_char,
        first_four,
        initials[0] + initials[1] + last_two,
        initials[0] + initials[1] + product_code
    ] + [initials[0] + initials[1] + comb for comb in random_combinations]
    potential_initials = remove_short_combinations(potential_initials)
    return potential_initials

def handle_four_or_more_words(words, product_group, existing_codes):
    initials = ''.join(word[0].upper() for word in words)
    first_three = ''.join(word[0].upper() for word in words[:3])
    first_four = ''.join(word[0].upper() for word in words[:4])
    product_code = product_group[:2].upper()
    last_two = words[-1][-2:]
    last_char = words[-1][-1]
    random_combinations = get_all_random_combinations(''.join(words), 2, {0, 1, 2})
    potential_initials = [
        first_four,
        initials[0] + initials[1] + initials[2] + initials[3],
        initials[0] + initials[1] + last_two,
        initials[0] + initials[1] + product_code
    ] + [initials[0] + initials[1] + comb for comb in random_combinations]
    potential_initials = remove_short_combinations(potential_initials)
    return potential_initials

def get_initials(string, existing_codes, product_group):
    cleaned_string = clean_string(string)
    words = cleaned_string.split()
    words = [word for word in words if word not in ['FOR', 'TO', 'AND', 'WITH', 'BY']]
    
    if len(words) == 1:
        potential_initials = handle_one_word(words, product_group, existing_codes)
    elif len(words) == 2:
        potential_initials = handle_two_words(words, product_group, existing_codes)
    elif len(words) == 3:
        potential_initials = handle_three_words(words, product_group, existing_codes)
    else:
        potential_initials = handle_four_or_more_words(words, product_group, existing_codes)
    
    for initials in potential_initials:
        if not is_duplicate(initials, existing_codes):
            existing_codes.add(initials)
            print(f"[INFO] Generated item code {initials} for addon: {' '.join(words)}")
            return initials.upper()
    
    print(f"[WARNING] Could not generate unique initials for: {' '.join(words)}")
    print(f"[DEBUG] Potential initials were: {potential_initials}")
    return None