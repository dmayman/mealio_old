"""Ingredient API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import Ingredient, IngredientCreate
from app.services import IngredientService

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.post("/", response_model=Ingredient, status_code=status.HTTP_201_CREATED)
async def create_ingredient(
    ingredient_data: IngredientCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new ingredient."""
    # Check if ingredient already exists
    existing = await IngredientService.get_ingredient_by_name(db, ingredient_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ingredient with this name already exists"
        )
    
    try:
        ingredient = await IngredientService.create_ingredient(db, ingredient_data)
        return ingredient
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create ingredient: {str(e)}"
        )


@router.get("/search", response_model=List[Ingredient])
async def search_ingredients(
    q: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Search ingredients by name."""
    if len(q.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be at least 2 characters long"
        )
    
    ingredients = await IngredientService.search_ingredients(db, q.strip(), limit)
    return ingredients


@router.get("/{ingredient_name}", response_model=Ingredient)
async def get_ingredient_by_name(
    ingredient_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get ingredient by name."""
    ingredient = await IngredientService.get_ingredient_by_name(db, ingredient_name)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found"
        )
    
    return ingredient