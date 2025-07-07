#!/usr/bin/env python3
"""Debug fraction handling."""

from ingredient_parser import parse_ingredient

ingredient_text = "1½ tablespoons mayonnaise"

print(f"Original: '{ingredient_text}'")
parsed = parse_ingredient(ingredient_text)

if parsed.amount and len(parsed.amount) > 0:
    amount = parsed.amount[0]
    print(f"Amount text: '{amount.text}'")
    print(f"Amount quantity: {amount.quantity}")
    print(f"Amount unit: {amount.unit}")

if parsed.name and len(parsed.name) > 0:
    name = parsed.name[0]
    print(f"Name text: '{name.text}'")
    print(f"Name starting index: {name.starting_index}")

# Test our extraction
name_position = ingredient_text.find("mayonnaise")
print(f"Name position in original: {name_position}")
print(f"Text from name position: '{ingredient_text[name_position:]}'")