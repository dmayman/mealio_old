"""Shopping list API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.schemas import ShoppingList, ShoppingListCreate, ShoppingListUpdate, ShoppingListItem, ShoppingListItemCreate, ShoppingListItemUpdate, APIResponse
from app.services import ShoppingListService
from app.models import User

router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])

# Mock dependency for current user - replace with actual auth
async def get_current_user() -> User:
    """Mock current user dependency."""
    # In production, this would extract user from JWT token
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        name="Test User"
    )


@router.post("/", response_model=ShoppingList, status_code=status.HTTP_201_CREATED)
async def create_shopping_list(
    shopping_list_data: ShoppingListCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new shopping list."""
    try:
        shopping_list = await ShoppingListService.create_shopping_list(db, current_user.id, shopping_list_data)
        return shopping_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create shopping list: {str(e)}"
        )


@router.get("/", response_model=List[ShoppingList])
async def get_user_shopping_lists(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get shopping lists for the current user."""
    shopping_lists = await ShoppingListService.get_user_shopping_lists(db, current_user.id)
    return shopping_lists


@router.get("/{shopping_list_id}", response_model=ShoppingList)
async def get_shopping_list(
    shopping_list_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific shopping list."""
    shopping_list = await ShoppingListService.get_shopping_list(db, shopping_list_id)
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    
    # Check if user owns the shopping list
    if shopping_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this shopping list"
        )
    
    return shopping_list


@router.post("/from-meal-plan/{meal_plan_id}", response_model=ShoppingList, status_code=status.HTTP_201_CREATED)
async def create_shopping_list_from_meal_plan(
    meal_plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a shopping list from a meal plan."""
    try:
        shopping_list = await ShoppingListService.generate_shopping_list_from_meal_plan(
            db, current_user.id, meal_plan_id
        )
        return shopping_list
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate shopping list: {str(e)}"
        )


@router.post("/{shopping_list_id}/items", response_model=ShoppingListItem, status_code=status.HTTP_201_CREATED)
async def add_shopping_list_item(
    shopping_list_id: uuid.UUID,
    item_data: ShoppingListItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add an item to a shopping list."""
    # Check if shopping list exists and user owns it
    shopping_list = await ShoppingListService.get_shopping_list(db, shopping_list_id)
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    
    if shopping_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this shopping list"
        )
    
    try:
        item = await ShoppingListService.add_shopping_list_item(db, shopping_list_id, item_data)
        return item
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add item: {str(e)}"
        )


@router.put("/items/{item_id}", response_model=ShoppingListItem)
async def update_shopping_list_item(
    item_id: uuid.UUID,
    item_data: ShoppingListItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a shopping list item."""
    # Get the item and check ownership through shopping list
    from sqlalchemy import select
    from app.models import ShoppingListItem as ShoppingListItemModel
    
    result = await db.execute(
        select(ShoppingListItemModel)
        .join(ShoppingListItemModel.shopping_list)
        .where(ShoppingListItemModel.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item not found"
        )
    
    if item.shopping_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this item"
        )
    
    updated_item = await ShoppingListService.update_shopping_list_item(db, item_id, item_data)
    return updated_item


@router.put("/{shopping_list_id}/items/{item_id}/check", response_model=ShoppingListItem)
async def toggle_item_checked(
    shopping_list_id: uuid.UUID,
    item_id: uuid.UUID,
    checked: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle the checked status of a shopping list item."""
    # Check ownership
    shopping_list = await ShoppingListService.get_shopping_list(db, shopping_list_id)
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    
    if shopping_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this shopping list"
        )
    
    # Update item
    item_data = ShoppingListItemUpdate(checked=checked)
    updated_item = await ShoppingListService.update_shopping_list_item(db, item_id, item_data)
    
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item not found"
        )
    
    return updated_item