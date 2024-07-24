# utils/string_handling.py
import base64
import re
import random

def encode_base64(string):
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')

def split_into_morphemes(word):
    # A very basic heuristic to split words into possible morphemes
    # This should be replaced by a more sophisticated NLP-based approach if available
    common_roots = ['work', 'log', 'conflu', 'table', 'form', 'survey', 'chart', 'filter', 'spreadsheet', 'menu', 'bot', 'draw']
    morphemes = []
    remaining = word.lower()

    for root in common_roots:
        if root in remaining:
            morphemes.append(root)
            remaining = remaining.replace(root, '', 1)
    
    # If remaining is not empty, add it as a separate morpheme
    if remaining:
        morphemes.append(remaining)

    return morphemes

def get_initials(string, existing_codes):
    # Remove non-letter characters and split the string into words
    words = re.sub(r'[^a-zA-Z\s]', '', string).split()

    morphemes = []
    for word in words:
        morphemes.extend(split_into_morphemes(word))

    # Generate initials using the first character of up to the first three morphemes
    if len(morphemes) >= 3:
        initials = ''.join(morpheme[0].upper() for morpheme in morphemes[:3])
    else:
        initials = ''.join(morpheme[0].upper() for morpheme in morphemes)
    
    # Ensure the initials are 3 characters long
    if len(initials) < 3:
        cleaned_string = ''.join(re.findall(r'[A-Za-z]', string)).upper()
        initials += cleaned_string[len(initials):len(initials) + (3 - len(initials))]

    # Ensure the initials are unique
    cleaned_string = ''.join(re.findall(r'[A-Za-z]', string)).upper()  # Clean the string to remove non-letter characters
    if initials in existing_codes:
        while initials in existing_codes:
            first_char = cleaned_string[0]
            remaining_chars = cleaned_string[1:]
            random_start = random.randint(0, len(remaining_chars) - 2)
            additional_chars = remaining_chars[random_start:random_start + 2]
            initials = first_char + additional_chars

    existing_codes.add(initials)
    return initials