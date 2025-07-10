"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
import uuid


# Base schemas
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# User schemas
class UserBase(BaseSchema):
    email: str = Field(..., max_length=255)
    name: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseSchema):
    name: Optional[str] = Field(None, max_length=255)


class User(UserBase):
    id: uuid.UUID
    current_household_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


# Household schemas
class HouseholdBase(BaseSchema):
    name: str = Field(..., max_length=255)


class HouseholdCreate(HouseholdBase):
    pass


class HouseholdUpdate(BaseSchema):
    name: Optional[str] = Field(None, max_length=255)


class Household(HouseholdBase):
    id: uuid.UUID
    created_by: uuid.UUID
    invite_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Household membership schemas first (to avoid forward reference issues)
class HouseholdMembershipBase(BaseSchema):
    role: str = Field(default="member", pattern="^(admin|member)$")


class HouseholdMembershipCreate(HouseholdMembershipBase):
    user_id: uuid.UUID


class HouseholdMembershipUpdate(BaseSchema):
    role: Optional[str] = Field(None, pattern="^(admin|member)$")


class HouseholdMembership(HouseholdMembershipBase):
    id: uuid.UUID
    household_id: uuid.UUID
    user_id: uuid.UUID
    joined_at: datetime
    user: Optional[User] = None


# Now we can define HouseholdWithMembers after HouseholdMembership is defined
class HouseholdWithMembers(Household):
    members: List[HouseholdMembership] = []


# Invite schemas
class HouseholdInviteCreate(BaseSchema):
    invite_code: str = Field(..., max_length=50)


class HouseholdJoinRequest(BaseSchema):
    invite_code: str = Field(..., max_length=50)


# Ingredient schemas
class IngredientBase(BaseSchema):
    name: str = Field(..., max_length=255)
    category: Optional[str] = Field(None, max_length=100)


class IngredientCreate(IngredientBase):
    pass


class Ingredient(IngredientBase):
    id: uuid.UUID
    created_at: datetime


# Recipe ingredient schemas
class RecipeIngredientBase(BaseSchema):
    ingredient_id: uuid.UUID
    quantity: Optional[Decimal] = None
    unit: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    order_index: int = 0


class RecipeIngredientCreate(RecipeIngredientBase):
    pass


class RecipeIngredient(RecipeIngredientBase):
    id: uuid.UUID
    recipe_id: uuid.UUID
    ingredient: Optional[Ingredient] = None


# Recipe schemas
class RecipeBase(BaseSchema):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    instructions: Optional[List[str]] = None
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    source_url: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)
    difficulty_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    source_type: str = Field(default="manual", pattern="^(scraped|manual|generated)$")
    shared_with_household: bool = Field(default=True)


class RecipeCreate(RecipeBase):
    ingredients: Optional[List[RecipeIngredientCreate]] = []


class RecipeUpdate(BaseSchema):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    instructions: Optional[List[str]] = None
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    source_url: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)
    difficulty_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    shared_with_household: Optional[bool] = None


class Recipe(RecipeBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    recipe_ingredients: Optional[List[RecipeIngredient]] = []


# Meal plan schemas
class MealPlanBase(BaseSchema):
    week_start: date
    name: Optional[str] = Field(None, max_length=255)


class MealPlanCreate(MealPlanBase):
    pass


class MealPlanUpdate(BaseSchema):
    name: Optional[str] = Field(None, max_length=255)


class MealPlan(MealPlanBase):
    id: uuid.UUID
    user_id: uuid.UUID
    household_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Planned meal schemas
class PlannedMealBase(BaseSchema):
    recipe_id: uuid.UUID
    planned_date: Optional[date] = None
    meal_type: str = Field(..., pattern="^(breakfast|lunch|dinner|snack)$")
    notes: Optional[str] = None


class PlannedMealCreate(PlannedMealBase):
    pass


class PlannedMealUpdate(BaseSchema):
    planned_date: Optional[date] = None
    meal_type: Optional[str] = Field(None, pattern="^(breakfast|lunch|dinner|snack)$")
    completed: Optional[bool] = None
    notes: Optional[str] = None


class PlannedMeal(PlannedMealBase):
    id: uuid.UUID
    meal_plan_id: uuid.UUID
    completed: bool
    created_at: datetime
    recipe: Optional[Recipe] = None


# Shopping list schemas
class ShoppingListBase(BaseSchema):
    name: str = Field(default="Shopping List", max_length=255)
    status: str = Field(default="active", pattern="^(active|completed|archived)$")


class ShoppingListCreate(BaseSchema):
    meal_plan_id: Optional[uuid.UUID] = None
    name: str = Field(default="Shopping List", max_length=255)


class ShoppingListUpdate(BaseSchema):
    name: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, pattern="^(active|completed|archived)$")


class ShoppingList(ShoppingListBase):
    id: uuid.UUID
    user_id: uuid.UUID
    household_id: uuid.UUID
    meal_plan_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


# Shopping list item schemas
class ShoppingListItemBase(BaseSchema):
    ingredient_id: uuid.UUID
    quantity: Optional[Decimal] = None
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    order_index: int = 0


class ShoppingListItemCreate(ShoppingListItemBase):
    pass


class ShoppingListItemUpdate(BaseSchema):
    quantity: Optional[Decimal] = None
    unit: Optional[str] = Field(None, max_length=50)
    checked: Optional[bool] = None
    category: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    order_index: Optional[int] = None


class ShoppingListItem(ShoppingListItemBase):
    id: uuid.UUID
    shopping_list_id: uuid.UUID
    checked: bool
    ingredient: Optional[Ingredient] = None


# Recipe usage schemas
class RecipeUsageBase(BaseSchema):
    recipe_id: uuid.UUID
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    cooking_time_actual: Optional[int] = Field(None, ge=0)


class RecipeUsageCreate(RecipeUsageBase):
    pass


class RecipeUsage(RecipeUsageBase):
    id: uuid.UUID
    user_id: uuid.UUID
    used_at: datetime
    recipe: Optional[Recipe] = None


# API Response schemas
class APIResponse(BaseSchema):
    success: bool
    message: str
    data: Optional[Dict[Any, Any]] = None


class PaginatedResponse(BaseSchema):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


# Recipe scraping schemas (from existing main.py)
class RecipeURL(BaseModel):
    url: str