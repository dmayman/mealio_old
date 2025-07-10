"""
Ingredient parsing service using ingredient-parser library.
Handles parsing raw ingredient strings into structured components.
"""

import logging
from typing import Dict, Optional, List
from ingredient_parser import parse_ingredient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import Ingredient

logger = logging.getLogger(__name__)

class IngredientParsingService:
    """Service for parsing ingredient strings into structured components."""
    
    @staticmethod
    def parse_ingredient_string(ingredient_text: str) -> Dict:
        """
        Parse a raw ingredient string into structured components.
        
        Args:
            ingredient_text: Raw ingredient string like "4 cups fresh corn kernels"
            
        Returns:
            Dict with parsed components and confidence score
        """
        try:
            parsed = parse_ingredient(ingredient_text)
            
            # Extract quantity and unit from amount
            quantity = None
            unit = None
            amount_confidence = 0.8
            
            if parsed.amount and len(parsed.amount) > 0:
                amount = parsed.amount[0]
                quantity = float(amount.quantity) if amount.quantity else None
                unit = str(amount.unit) if amount.unit else None
                amount_confidence = amount.confidence
            
            # Extract ingredient name
            ingredient_name = None
            name_confidence = 0.8
            
            if parsed.name and len(parsed.name) > 0:
                name = parsed.name[0]
                ingredient_name = name.text if name.text else None
                name_confidence = name.confidence
            
            # Extract comment/preparation notes
            notes = None
            if parsed.comment:
                notes = parsed.comment.text if hasattr(parsed.comment, 'text') else str(parsed.comment)
            elif parsed.preparation:
                notes = parsed.preparation.text if hasattr(parsed.preparation, 'text') else str(parsed.preparation)
            
            # Calculate overall confidence (average of components)
            overall_confidence = (amount_confidence + name_confidence) / 2
            
            result = {
                "quantity": quantity,
                "unit": unit,
                "ingredient_name": ingredient_name.strip().lower() if ingredient_name else None,
                "notes": notes,
                "raw_text": ingredient_text,
                "parsing_confidence": overall_confidence,
                "parsed_successfully": True
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Failed to parse ingredient '{ingredient_text}': {str(e)}")
            
            # Return fallback parsing
            return {
                "quantity": None,
                "unit": None,
                "ingredient_name": ingredient_text.strip().lower(),
                "notes": None,
                "raw_text": ingredient_text,
                "parsing_confidence": 0.1,  # Low confidence for fallback
                "parsed_successfully": False
            }
    
    @staticmethod
    async def find_or_create_ingredient(db: AsyncSession, ingredient_name: str) -> Optional[Ingredient]:
        """
        Find an existing ingredient by name or create a new one.
        
        Args:
            db: Database session
            ingredient_name: Name of the ingredient to find/create
            
        Returns:
            Ingredient model instance or None if creation fails
        """
        if not ingredient_name:
            return None
            
        # Normalize ingredient name
        normalized_name = ingredient_name.strip().lower()
        
        # Try to find existing ingredient
        result = await db.execute(
            select(Ingredient).where(Ingredient.name == normalized_name)
        )
        existing_ingredient = result.scalars().first()
        
        if existing_ingredient:
            return existing_ingredient
        
        # Create new ingredient
        try:
            new_ingredient = Ingredient(
                name=normalized_name,
                category=None  # Could be enhanced to auto-categorize
            )
            db.add(new_ingredient)
            await db.commit()
            await db.refresh(new_ingredient)
            return new_ingredient
            
        except Exception as e:
            logger.error(f"Failed to create ingredient '{normalized_name}': {str(e)}")
            await db.rollback()
            return None
    
    @staticmethod
    def parse_ingredients_batch(ingredient_texts: List[str]) -> List[Dict]:
        """
        Parse multiple ingredient strings in batch.
        
        Args:
            ingredient_texts: List of raw ingredient strings
            
        Returns:
            List of parsed ingredient dictionaries
        """
        parsed_ingredients = []
        
        for ingredient_text in ingredient_texts:
            if ingredient_text and ingredient_text.strip():
                parsed = IngredientParsingService.parse_ingredient_string(ingredient_text)
                parsed_ingredients.append(parsed)
        
        return parsed_ingredients
    
    @staticmethod
    def get_parsing_stats(parsed_ingredients: List[Dict]) -> Dict:
        """
        Get statistics about parsing success rate.
        
        Args:
            parsed_ingredients: List of parsed ingredient dictionaries
            
        Returns:
            Dict with parsing statistics
        """
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