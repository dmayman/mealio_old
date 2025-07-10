#!/usr/bin/env python3
"""Debug unit handling."""

from ingredient_parser import parse_ingredient

test_cases = [
    "2 tablespoons pizza sauce",
    "1/4 cup mozzarella cheese", 
    "4 cups fresh corn",
    "1 tablespoon olive oil"
]

for ingredient_text in test_cases:
    print(f"\nIngredient: {ingredient_text}")
    parsed = parse_ingredient(ingredient_text)
    
    if parsed.amount and len(parsed.amount) > 0:
        amount = parsed.amount[0]
        print(f"  Quantity: {amount.quantity}")
        print(f"  Unit: {amount.unit}")
        print(f"  Unit type: {type(amount.unit)}")
        print(f"  Amount text: {amount.text}")