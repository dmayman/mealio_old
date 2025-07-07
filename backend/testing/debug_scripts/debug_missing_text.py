#!/usr/bin/env python3
"""Debug missing parenthetical text."""

from ingredient_parser import parse_ingredient
import re

ingredient_text = "4 cups fresh corn kernels (from about 4 ears)"

print(f"Original: {ingredient_text}")
parsed = parse_ingredient(ingredient_text)

print(f"\nParsed components:")
print(f"  Amount: {parsed.amount}")
if parsed.amount:
    print(f"    Text: {parsed.amount[0].text}")
    print(f"    Starting index: {parsed.amount[0].starting_index}")

print(f"  Name: {parsed.name}")
if parsed.name:
    for i, name in enumerate(parsed.name):
        print(f"    Name {i}: {name.text} (index: {name.starting_index})")

print(f"  Comment: {parsed.comment}")
print(f"  Preparation: {parsed.preparation}")
print(f"  Purpose: {parsed.purpose}")

# Simulate the current parsing logic
cleaned_text = ingredient_text

# First remove parenthetical content that might be notes
print(f"\nBefore removing parentheses: {cleaned_text}")
cleaned_text = re.sub(r'\([^)]*\)', '', cleaned_text).strip()
print(f"After removing parentheses: {cleaned_text}")

# Find the first ingredient name and extract text starting from there
if parsed.name and len(parsed.name) > 0:
    first_name = parsed.name[0]
    name_text = first_name.text
    print(f"First name text: '{name_text}'")
    if name_text and name_text in ingredient_text:
        name_position = ingredient_text.find(name_text)
        print(f"Name position in original: {name_position}")
        if name_position >= 0:
            cleaned_text = ingredient_text[name_position:].strip()
            print(f"Text from name position: '{cleaned_text}'")
            cleaned_text = re.sub(r'\([^)]*\)', '', cleaned_text).strip()
            print(f"After removing parentheses again: '{cleaned_text}'")