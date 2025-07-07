#!/usr/bin/env python3
"""
Test ingredient parsing with scraped recipe examples.
"""

import json
import asyncio
from app.ingredient_parser_service import IngredientParsingService


async def test_ingredient_parsing():
    """Test ingredient parsing with examples from scraped recipes."""
    
    # Load scraped recipe examples
    with open('scraped_recipe_15-minute-garlic-bre.json', 'r') as f:
        recipe1 = json.load(f)
    
    with open('scraped_recipe_1025361-oven-seared-.json', 'r') as f:
        recipe2 = json.load(f)
    
    print("=== Testing Ingredient Parsing ===\n")
    
    # Test recipe 1 ingredients
    print("Recipe 1: 15-Minute Garlic Bread Pizza")
    print("Original ingredients:")
    for i, ingredient in enumerate(recipe1['ingredients'][:5]):  # First 5 ingredients
        print(f"  {i+1}. {ingredient}")
    
    print("\nParsed ingredients:")
    parsed_ingredients_1 = IngredientParsingService.parse_ingredients_batch(recipe1['ingredients'][:5])
    for i, parsed in enumerate(parsed_ingredients_1):
        print(f"  {i+1}. Raw: '{parsed['raw_text']}'")
        print(f"     Parsed: {parsed['quantity']} {parsed['unit']} {parsed['ingredient_name']}")
        print(f"     Notes: {parsed['notes']}")
        print(f"     Confidence: {parsed['parsing_confidence']:.2f}")
        print(f"     Success: {parsed['parsed_successfully']}")
        print()
    
    # Test recipe 2 ingredients
    print("\n" + "="*50)
    print("Recipe 2: Oven-Seared Salmon With Corn and Tomatoes")
    print("Original ingredients:")
    for i, ingredient in enumerate(recipe2['ingredients'][:5]):  # First 5 ingredients
        print(f"  {i+1}. {ingredient}")
    
    print("\nParsed ingredients:")
    parsed_ingredients_2 = IngredientParsingService.parse_ingredients_batch(recipe2['ingredients'][:5])
    for i, parsed in enumerate(parsed_ingredients_2):
        print(f"  {i+1}. Raw: '{parsed['raw_text']}'")
        print(f"     Parsed: {parsed['quantity']} {parsed['unit']} {parsed['ingredient_name']}")
        print(f"     Notes: {parsed['notes']}")
        print(f"     Confidence: {parsed['parsing_confidence']:.2f}")
        print(f"     Success: {parsed['parsed_successfully']}")
        print()
    
    # Get parsing statistics
    all_parsed = parsed_ingredients_1 + parsed_ingredients_2
    stats = IngredientParsingService.get_parsing_stats(all_parsed)
    
    print("\n" + "="*50)
    print("Parsing Statistics:")
    print(f"Total ingredients: {stats['total']}")
    print(f"Successfully parsed: {stats['parsed_successfully']}")
    print(f"Success rate: {stats['success_rate']:.1%}")
    print(f"Average confidence: {stats['average_confidence']:.2f}")


if __name__ == "__main__":
    asyncio.run(test_ingredient_parsing())