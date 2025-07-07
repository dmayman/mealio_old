"""Meal plan API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.schemas import MealPlan, MealPlanCreate, MealPlanUpdate, PlannedMeal, PlannedMealCreate, PlannedMealUpdate, APIResponse
from app.services import MealPlanService
from app.models import User

router = APIRouter(prefix="/meal-plans", tags=["meal-plans"])

# Mock dependency for current user - replace with actual auth
async def get_current_user() -> User:
    """Mock current user dependency."""
    # In production, this would extract user from JWT token
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        name="Test User"
    )


@router.post("/", response_model=MealPlan, status_code=status.HTTP_201_CREATED)
async def create_meal_plan(
    meal_plan_data: MealPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new meal plan."""
    try:
        meal_plan = await MealPlanService.create_meal_plan(db, current_user.id, meal_plan_data)
        return meal_plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create meal plan: {str(e)}"
        )


@router.get("/", response_model=List[MealPlan])
async def get_user_meal_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get meal plans for the current user."""
    meal_plans = await MealPlanService.get_user_meal_plans(db, current_user.id)
    return meal_plans


@router.get("/{meal_plan_id}", response_model=MealPlan)
async def get_meal_plan(
    meal_plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific meal plan."""
    meal_plan = await MealPlanService.get_meal_plan(db, meal_plan_id)
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    # Check if user owns the meal plan
    if meal_plan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this meal plan"
        )
    
    return meal_plan


@router.post("/{meal_plan_id}/meals", response_model=PlannedMeal, status_code=status.HTTP_201_CREATED)
async def add_planned_meal(
    meal_plan_id: uuid.UUID,
    planned_meal_data: PlannedMealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a planned meal to a meal plan."""
    # Check if meal plan exists and user owns it
    meal_plan = await MealPlanService.get_meal_plan(db, meal_plan_id)
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    if meal_plan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this meal plan"
        )
    
    try:
        planned_meal = await MealPlanService.add_planned_meal(db, meal_plan_id, planned_meal_data)
        return planned_meal
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add planned meal: {str(e)}"
        )


@router.put("/meals/{planned_meal_id}", response_model=PlannedMeal)
async def update_planned_meal(
    planned_meal_id: uuid.UUID,
    planned_meal_data: PlannedMealUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a planned meal."""
    # Get the planned meal and check ownership through meal plan
    from sqlalchemy import select
    from app.models import PlannedMeal as PlannedMealModel
    
    result = await db.execute(
        select(PlannedMealModel)
        .join(PlannedMealModel.meal_plan)
        .where(PlannedMealModel.id == planned_meal_id)
    )
    planned_meal = result.scalar_one_or_none()
    
    if not planned_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planned meal not found"
        )
    
    if planned_meal.meal_plan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this planned meal"
        )
    
    updated_planned_meal = await MealPlanService.update_planned_meal(db, planned_meal_id, planned_meal_data)
    return updated_planned_meal