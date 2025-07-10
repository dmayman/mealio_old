"""Recipe API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.schemas import Recipe, RecipeCreate, RecipeUpdate, APIResponse
from app.services import RecipeService, RecipeUsageService
from app.models import User

router = APIRouter(prefix="/recipes", tags=["recipes"])

# Mock dependency for current user - replace with actual auth
async def get_current_user() -> User:
    """Mock current user dependency."""
    # In production, this would extract user from JWT token
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        name="Test User"
    )


@router.post("/", response_model=Recipe, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe_data: RecipeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new recipe."""
    try:
        recipe = await RecipeService.create_recipe(db, current_user.id, recipe_data)
        return recipe
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create recipe: {str(e)}"
        )


@router.get("/", response_model=List[Recipe])
async def get_accessible_recipes(
    limit: int = 50,
    offset: int = 0,
    include_household: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recipes accessible to the current user."""
    if include_household:
        recipes = await RecipeService.get_household_recipes(db, current_user.id, limit, offset)
    else:
        recipes = await RecipeService.get_user_recipes(db, current_user.id, limit, offset)
    return recipes


@router.get("/mine", response_model=List[Recipe])
async def get_my_recipes(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get only the current user's own recipes."""
    recipes = await RecipeService.get_user_recipes(db, current_user.id, limit, offset)
    return recipes


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(
    recipe_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific recipe."""
    recipe = await RecipeService.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Check if user can access the recipe (using new access model)
    can_access = await RecipeService.can_user_access_recipe(db, recipe_id, current_user.id)
    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this recipe"
        )
    
    return recipe


@router.put("/{recipe_id}", response_model=Recipe)
async def update_recipe(
    recipe_id: uuid.UUID,
    recipe_data: RecipeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a recipe."""
    # Check if recipe exists
    recipe = await RecipeService.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Check if user can edit the recipe (using new access model)
    can_edit = await RecipeService.can_user_edit_recipe(db, recipe_id, current_user.id)
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this recipe"
        )
    
    updated_recipe = await RecipeService.update_recipe(db, recipe_id, recipe_data)
    return updated_recipe


@router.delete("/{recipe_id}", response_model=APIResponse)
async def delete_recipe(
    recipe_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a recipe."""
    # Check if recipe exists
    recipe = await RecipeService.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Check if user can edit the recipe (using new access model)
    can_edit = await RecipeService.can_user_edit_recipe(db, recipe_id, current_user.id)
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this recipe"
        )
    
    success = await RecipeService.delete_recipe(db, recipe_id)
    if success:
        return APIResponse(success=True, message="Recipe deleted successfully")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete recipe"
        )


@router.get("/{recipe_id}/stats")
async def get_recipe_stats(
    recipe_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get usage statistics for a recipe."""
    # Check if recipe exists
    recipe = await RecipeService.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Check if user can edit the recipe (stats should only be visible to owner)
    can_edit = await RecipeService.can_user_edit_recipe(db, recipe_id, current_user.id)
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this recipe's statistics"
        )
    
    stats = await RecipeUsageService.get_recipe_usage_stats(db, recipe_id)
    return stats


@router.post("/{recipe_id}/copy", response_model=Recipe, status_code=status.HTTP_201_CREATED)
async def copy_recipe(
    recipe_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Copy a recipe for the current user."""
    # Check if recipe exists
    original_recipe = await RecipeService.get_recipe(db, recipe_id)
    if not original_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Check if user can access the recipe (using new access model)
    can_access = await RecipeService.can_user_access_recipe(db, recipe_id, current_user.id)
    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this recipe"
        )
    
    # Copy the recipe
    try:
        copied_recipe = await RecipeService.copy_recipe(db, recipe_id, current_user.id)
        if not copied_recipe:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to copy recipe"
            )
        return copied_recipe
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to copy recipe: {str(e)}"
        )