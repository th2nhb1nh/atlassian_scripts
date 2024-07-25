# utils/string_handling.py
import base64
import random
import re

def encode_base64(string):
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')

def is_duplicate(initials, existing_codes):
    return initials in existing_codes

def get_random_letters(string, count, exclude_indices):
    available_indices = [i for i in range(len(string)) if i not in exclude_indices]
    return ''.join(string[i] for i in random.sample(available_indices, count))

def handle_one_word(words, product_group, existing_codes):
    first_two = words[0][:2]
    # product_letter = product_group[0].upper()
    last_two = words[0][-2:]
    # random_letters = get_random_letters(words[0], 2, {0, 1})
    potential_initials = [
        first_two + product_group[:2],
        # first_two + product_letter,
        first_two + last_two,
        # first_two + random_letters
    ]

    for initials in potential_initials:
        if not is_duplicate(initials, existing_codes):
            existing_codes.add(initials)
            return initials
    return None

def handle_two_words(words, product_group, existing_codes):
    first_two = words[0][:2]
    initials = ''.join(word[0].upper() for word in words)
    last_two = words[1][-2:]
    random_letters = get_random_letters(''.join(words), 2, {0, 1, len(words[0])})
    # product_letter = product_group[0].upper()
    potential_initials = [
        first_two + product_group[:2],
        initials[0] + initials[1] + last_two,
        first_two + random_letters
    ]

    for initials in potential_initials:
        if not is_duplicate(initials, existing_codes):
            existing_codes.add(initials)
            return initials
    return None

def handle_three_words(words, existing_codes):
    initials = ''.join(word[0].upper() for word in words)
    last_two = words[-1][-2:]
    last_char = words[-1][-1]
    random_letters = get_random_letters(''.join(words), 2, {0, 1, 2})
    potential_initials = [
        initials,
        initials[0] + initials[1] + last_two,
        initials[0] + initials[1] + initials[2] + last_char,
        words[0][:2] + random_letters
    ]

    for initials in potential_initials:
        if not is_duplicate(initials, existing_codes):
            existing_codes.add(initials)
            return initials
    return None

def handle_four_or_more_words(words, existing_codes):
    first_three = ''.join(word[0].upper() for word in words[:3])
    first_four = ''.join(word[0].upper() for word in words[:4])
    last_two = words[-1][-2:]
    random_letters = get_random_letters(''.join(words), 2, {0, 1, 2})
    potential_initials = [
        first_four,
        first_three + last_two,
        words[0][:2] + random_letters
    ]

    for initials in potential_initials:
        if not is_duplicate(initials, existing_codes):
            existing_codes.add(initials)
            return initials
    return None

def get_initials(string, existing_codes, product_group):
    words = re.findall(r"[\w']+", string)
    # Remove "for" and "to" from words
    words = [word for word in words if word.lower() not in ['for', 'to', 'and', 'with', 'by']]
    print(words)
    print(len(words))

    if len(words) == 1:
        initials = handle_one_word(words, product_group, existing_codes)
    elif len(words) == 2:
        initials = handle_two_words(words, product_group, existing_codes)
    elif len(words) == 3:
        initials = handle_three_words(words, existing_codes)
    else:
        initials = handle_four_or_more_words(words, existing_codes)
    print(initials)

    if not initials:
        return None

    return initials.upper()