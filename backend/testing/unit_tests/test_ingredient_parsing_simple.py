#!/usr/bin/env python3
"""
Test ingredient parsing with scraped recipe examples (standalone version).
"""

import json
from ingredient_parser import parse_ingredient


def parse_ingredient_string(ingredient_text: str) -> dict:
    """Parse a raw ingredient string into structured components."""
    try:
        parsed = parse_ingredient(ingredient_text)
        
        # Extract quantity and unit from amount
        quantity_str = None  # Combined text for UI (e.g., "2 tablespoons")
        quantity_value = None  # Numeric value for scaling (e.g., 2.0)
        unit = None  # Unit string for scaling (e.g., "tablespoon")
        amount_confidence = 0.8
        
        if parsed.amount and len(parsed.amount) > 0:
            amount = parsed.amount[0]
            
            # Combined text for UI display (has correct pluralization)
            quantity_str = amount.text if amount.text else None
            
            # Individual components for functionality
            quantity_value = float(amount.quantity) if amount.quantity else None
            unit = str(amount.unit) if amount.unit else None
            
            amount_confidence = amount.confidence
        
        # Extract notes from preparation, comment, or purpose
        notes_parts = []
        if parsed.preparation:
            if hasattr(parsed.preparation, 'text') and parsed.preparation.text:
                notes_parts.append(parsed.preparation.text)
            elif isinstance(parsed.preparation, list):
                for prep in parsed.preparation:
                    if hasattr(prep, 'text') and prep.text:
                        notes_parts.append(prep.text)
        
        if parsed.comment:
            comment_text = parsed.comment.text if hasattr(parsed.comment, 'text') else str(parsed.comment)
            if comment_text:
                notes_parts.append(comment_text)
        
        if parsed.purpose:
            purpose_text = parsed.purpose.text if hasattr(parsed.purpose, 'text') else str(parsed.purpose)
            if purpose_text:
                notes_parts.append(purpose_text)
        
        notes = ", ".join(notes_parts) if notes_parts else None
        
        # Create cleaned ingredient text by finding the first ingredient name
        import re
        cleaned_text = ingredient_text
        
        # Find the first ingredient name and extract text starting from there
        if parsed.name and len(parsed.name) > 0:
            first_name = parsed.name[0]
            name_text = first_name.text
            if name_text and name_text in ingredient_text:
                # Find where the ingredient name actually starts in the original text
                name_position = ingredient_text.find(name_text)
                if name_position >= 0:
                    cleaned_text = ingredient_text[name_position:].strip()
        
        # Only remove parenthetical content if it was captured as notes
        # Otherwise, preserve it as it might contain useful information
        captured_parenthetical_content = []
        for note_part in notes_parts:
            if note_part and '(' in ingredient_text and note_part in ingredient_text:
                # Find parenthetical content that matches this note
                import re
                paren_matches = re.findall(r'\([^)]*\)', ingredient_text)
                for match in paren_matches:
                    if note_part in match:
                        captured_parenthetical_content.append(match)
        
        # Remove only the parenthetical content that was captured as notes
        for captured in captured_parenthetical_content:
            cleaned_text = cleaned_text.replace(captured, '').strip()
        
        # Remove notes from the text
        for note_part in notes_parts:
            if note_part and note_part in cleaned_text:
                cleaned_text = cleaned_text.replace(note_part, "").strip()
        
        # Remove trailing comma and space
        cleaned_text = cleaned_text.rstrip(", ")
        
        # Clean up extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # Extract name confidence
        name_confidence = 0.8
        if parsed.name and len(parsed.name) > 0:
            name_confidence = parsed.name[0].confidence
        
        # Calculate overall confidence (average of components)
        overall_confidence = (amount_confidence + name_confidence) / 2
        
        result = {
            "quantity": quantity_str,  # Combined for UI: "2 tablespoons"
            "quantity_value": quantity_value,  # Numeric for scaling: 2.0
            "unit": unit,  # Unit for scaling: "tablespoon"
            "text": cleaned_text,
            "notes": notes,
            "raw_text": ingredient_text,
            "parsing_confidence": overall_confidence,
            "parsed_successfully": True
        }
        
        return result
        
    except Exception as e:
        print(f"Failed to parse ingredient '{ingredient_text}': {str(e)}")
        
        # Return fallback parsing
        return {
            "quantity": None,
            "quantity_value": None,
            "unit": None,
            "text": ingredient_text.strip(),
            "notes": None,
            "raw_text": ingredient_text,
            "parsing_confidence": 0.1,  # Low confidence for fallback
            "parsed_successfully": False
        }


def parse_ingredients_batch(ingredient_texts: list) -> list:
    """Parse multiple ingredient strings in batch."""
    parsed_ingredients = []
    
    for ingredient_text in ingredient_texts:
        if ingredient_text and ingredient_text.strip():
            parsed = parse_ingredient_string(ingredient_text)
            parsed_ingredients.append(parsed)
    
    return parsed_ingredients


def get_parsing_stats(parsed_ingredients: list) -> dict:
    """Get statistics about parsing success rate."""
    total_count = len(parsed_ingredients)
    if total_count == 0:
        return {"total": 0, "parsed_successfully": 0, "success_rate": 0.0}
    
    successful_count = sum(1 for p in parsed_ingredients if p.get("parsed_successfully", False))
    avg_confidence = sum(p.get("parsing_confidence", 0) for p in parsed_ingredients) / total_count
    
    return {
        "total": total_count,
        "parsed_successfully": successful_count,
        "success_rate": successful_count / total_count,
        "average_confidence": avg_confidence
    }


def test_ingredient_parsing():
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
    parsed_ingredients_1 = parse_ingredients_batch(recipe1['ingredients'][:5])
    for i, parsed in enumerate(parsed_ingredients_1):
        print(f"  {i+1}. Raw: '{parsed['raw_text']}'")
        print(f"     Result: [{parsed['quantity']}] [{parsed['text']}] [{parsed['notes']}]")
        print(f"     Scaling: quantity={parsed['quantity_value']}, unit='{parsed['unit']}'")
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
    parsed_ingredients_2 = parse_ingredients_batch(recipe2['ingredients'][:5])
    for i, parsed in enumerate(parsed_ingredients_2):
        print(f"  {i+1}. Raw: '{parsed['raw_text']}'")
        print(f"     Result: [{parsed['quantity']}] [{parsed['text']}] [{parsed['notes']}]")
        print(f"     Scaling: quantity={parsed['quantity_value']}, unit='{parsed['unit']}'")
        print(f"     Confidence: {parsed['parsing_confidence']:.2f}")
        print(f"     Success: {parsed['parsed_successfully']}")
        print()
    
    # Get parsing statistics
    all_parsed = parsed_ingredients_1 + parsed_ingredients_2
    stats = get_parsing_stats(all_parsed)
    
    print("\n" + "="*50)
    print("Parsing Statistics:")
    print(f"Total ingredients: {stats['total']}")
    print(f"Successfully parsed: {stats['parsed_successfully']}")
    print(f"Success rate: {stats['success_rate']:.1%}")
    print(f"Average confidence: {stats['average_confidence']:.2f}")
    
    


if __name__ == "__main__":
    test_ingredient_parsing()