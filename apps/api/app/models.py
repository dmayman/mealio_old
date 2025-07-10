"""SQLAlchemy models for Mealio database."""

from sqlalchemy import Column, String, Integer, Text, DECIMAL, Boolean, DateTime, Date, ForeignKey, ARRAY, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    current_household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    recipes = relationship("Recipe", back_populates="user", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")
    shopping_lists = relationship("ShoppingList", back_populates="user", cascade="all, delete-orphan")
    recipe_usage = relationship("RecipeUsage", back_populates="user", cascade="all, delete-orphan")
    
    # Household relationships
    current_household = relationship("Household", foreign_keys=[current_household_id])
    created_households = relationship("Household", foreign_keys="Household.created_by", back_populates="creator")
    household_memberships = relationship("HouseholdMembership", back_populates="user", cascade="all, delete-orphan")


class Household(Base):
    """Household model."""
    __tablename__ = "households"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    invite_code = Column(String(50), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_households")
    members = relationship("HouseholdMembership", back_populates="household", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="household", cascade="all, delete-orphan")
    shopping_lists = relationship("ShoppingList", back_populates="household", cascade="all, delete-orphan")
    recipe_access = relationship("RecipeHouseholdAccess", back_populates="household", cascade="all, delete-orphan")


class HouseholdMembership(Base):
    """Household membership model."""
    __tablename__ = "household_memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), default="member")
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'member')", name="check_role"),
        UniqueConstraint("user_id", name="unique_user_household"),
    )

    # Relationships
    household = relationship("Household", back_populates="members")
    user = relationship("User", back_populates="household_memberships")


class Ingredient(Base):
    """Ingredient model."""
    __tablename__ = "ingredients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    category = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    recipe_ingredients = relationship("RecipeIngredient", back_populates="ingredient")
    shopping_list_items = relationship("ShoppingListItem", back_populates="ingredient")


class Recipe(Base):
    """Recipe model."""
    __tablename__ = "recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    instructions = Column(ARRAY(Text))
    prep_time = Column(Integer)  # minutes
    cook_time = Column(Integer)  # minutes
    servings = Column(Integer)
    source_url = Column(String(500))
    image_url = Column(String(500))
    difficulty_level = Column(String(20))
    source_type = Column(String(20), default='manual')
    shared_with_household = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint("difficulty_level IN ('beginner', 'intermediate', 'advanced')", name="check_difficulty_level"),
        CheckConstraint("source_type IN ('scraped', 'manual', 'generated')", name="check_source_type"),
    )

    # Relationships
    user = relationship("User", back_populates="recipes")
    recipe_ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    planned_meals = relationship("PlannedMeal", back_populates="recipe")
    recipe_usage = relationship("RecipeUsage", back_populates="recipe", cascade="all, delete-orphan")
    household_access = relationship("RecipeHouseholdAccess", back_populates="recipe", cascade="all, delete-orphan")


class RecipeIngredient(Base):
    """Recipe ingredients junction table."""
    __tablename__ = "recipe_ingredients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(DECIMAL(10, 2))
    unit = Column(String(50))
    notes = Column(Text)
    order_index = Column(Integer, default=0)

    # Relationships
    recipe = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")


class MealPlan(Base):
    """Meal plan model."""
    __tablename__ = "meal_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    week_start = Column(Date, nullable=False)
    name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="meal_plans")
    household = relationship("Household", back_populates="meal_plans")
    planned_meals = relationship("PlannedMeal", back_populates="meal_plan", cascade="all, delete-orphan")
    shopping_lists = relationship("ShoppingList", back_populates="meal_plan")


class PlannedMeal(Base):
    """Planned meal model."""
    __tablename__ = "planned_meals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meal_plan_id = Column(UUID(as_uuid=True), ForeignKey("meal_plans.id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id"), nullable=False)
    planned_date = Column(Date)
    meal_type = Column(String(50))
    completed = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint("meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')", name="check_meal_type"),
    )

    # Relationships
    meal_plan = relationship("MealPlan", back_populates="planned_meals")
    recipe = relationship("Recipe", back_populates="planned_meals")


class ShoppingList(Base):
    """Shopping list model."""
    __tablename__ = "shopping_lists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meal_plan_id = Column(UUID(as_uuid=True), ForeignKey("meal_plans.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), default='Shopping List')
    status = Column(String(20), default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'completed', 'archived')", name="check_status"),
    )

    # Relationships
    user = relationship("User", back_populates="shopping_lists")
    household = relationship("Household", back_populates="shopping_lists")
    meal_plan = relationship("MealPlan", back_populates="shopping_lists")
    shopping_list_items = relationship("ShoppingListItem", back_populates="shopping_list", cascade="all, delete-orphan")


class ShoppingListItem(Base):
    """Shopping list item model."""
    __tablename__ = "shopping_list_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shopping_list_id = Column(UUID(as_uuid=True), ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(DECIMAL(10, 2))
    unit = Column(String(50))
    checked = Column(Boolean, default=False)
    category = Column(String(100))
    notes = Column(Text)
    order_index = Column(Integer, default=0)

    # Relationships
    shopping_list = relationship("ShoppingList", back_populates="shopping_list_items")
    ingredient = relationship("Ingredient", back_populates="shopping_list_items")


class RecipeUsage(Base):
    """Recipe usage tracking model."""
    __tablename__ = "recipe_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    used_at = Column(DateTime(timezone=True), server_default=func.now())
    rating = Column(Integer)
    notes = Column(Text)
    cooking_time_actual = Column(Integer)  # actual cooking time in minutes

    # Constraints
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating"),
    )

    # Relationships
    user = relationship("User", back_populates="recipe_usage")
    recipe = relationship("Recipe", back_populates="recipe_usage")


class RecipeHouseholdAccess(Base):
    """Recipe household access tracking model."""
    __tablename__ = "recipe_household_access"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (
        UniqueConstraint("recipe_id", "household_id", name="unique_recipe_household_access"),
    )

    # Relationships
    recipe = relationship("Recipe", back_populates="household_access")
    household = relationship("Household", back_populates="recipe_access")
    granted_by_user = relationship("User", foreign_keys=[granted_by])