import base64
import itertools
import random
import re

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
        # first_three + product_group[:1].upper()
    ]

    for initials in potential_initials:
        if not is_duplicate(initials, existing_codes):
            return initials
    return None

def handle_two_words(words, product_group, existing_codes):
    first_two = words[0][:2]
    first_four = ''.join(word[0].upper() for word in words[:4])
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

    for initials in potential_initials:
        if not is_duplicate(initials, existing_codes):
            return initials
    return None

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

    for initials in potential_initials:
        if not is_duplicate(initials, existing_codes):
            return initials
    return None

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
        # first_three + last_char,
        initials[0] + initials[1] + initials[2] + initials[3],
        initials[0] + initials[1] + last_two,
        initials[0] + initials[1] + product_code
    ] + [initials[0] + initials[1] + comb for comb in random_combinations]

    for initials in potential_initials:
        if not is_duplicate(initials, existing_codes):
            return initials
    return None

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
