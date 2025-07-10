#!/usr/bin/env python3
"""
Debug ingredient parsing to understand the API structure.
"""

from ingredient_parser import parse_ingredient
import pprint

def debug_parsing():
    """Debug the structure of parsed ingredients."""
    
    test_ingredients = [
        "2 tablespoons pizza sauce",
        "4 cups fresh corn kernels",
        "1½ tablespoons mayonnaise"
    ]
    
    for ingredient_text in test_ingredients:
        print(f"\n=== Parsing: '{ingredient_text}' ===")
        try:
            parsed = parse_ingredient(ingredient_text)
            print(f"Type: {type(parsed)}")
            print(f"Dir: {dir(parsed)}")
            print(f"Parsed result:")
            pprint.pprint(vars(parsed))
            
            # Try different attribute access methods
            if hasattr(parsed, 'quantity'):
                print(f"Quantity: {parsed.quantity}")
            if hasattr(parsed, 'unit'):
                print(f"Unit: {parsed.unit}")
            if hasattr(parsed, 'name'):
                print(f"Name: {parsed.name}")
            if hasattr(parsed, 'comment'):
                print(f"Comment: {parsed.comment}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_parsing()