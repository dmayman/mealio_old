"""Service layer for database operations."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, union
from sqlalchemy.orm import selectinload
import uuid
import secrets
import string

from app.models import User, Recipe, Ingredient, RecipeIngredient, MealPlan, PlannedMeal, ShoppingList, ShoppingListItem, RecipeUsage, Household, HouseholdMembership, RecipeHouseholdAccess
from app.enhanced_models import RecipeNutrition, RecipeEquipment
from app.schemas import (
    UserCreate, UserUpdate, RecipeCreate, RecipeUpdate, 
    IngredientCreate, MealPlanCreate, MealPlanUpdate,
    PlannedMealCreate, PlannedMealUpdate, ShoppingListCreate, ShoppingListUpdate,
    ShoppingListItemCreate, ShoppingListItemUpdate, RecipeUsageCreate,
    HouseholdCreate, HouseholdUpdate, HouseholdMembershipCreate, HouseholdMembershipUpdate
)
from app.ingredient_parser_service import IngredientParsingService


class UserService:
    """Service for user operations."""
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user."""
        user = User(**user_data.model_dump())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def get_user(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user(db: AsyncSession, user_id: uuid.UUID, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        user = await UserService.get_user(db, user_id)
        if not user:
            return None
        
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user


class HouseholdService:
    """Service for household operations."""
    
    @staticmethod
    def generate_invite_code(length: int = 8) -> str:
        """Generate a random invite code."""
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    @staticmethod
    async def create_household(db: AsyncSession, user_id: uuid.UUID, household_data: HouseholdCreate) -> Household:
        """Create a new household and add the creator as admin."""
        # Generate unique invite code
        invite_code = HouseholdService.generate_invite_code()
        while await HouseholdService.get_household_by_invite_code(db, invite_code):
            invite_code = HouseholdService.generate_invite_code()
        
        # Create household
        household = Household(
            created_by=user_id,
            invite_code=invite_code,
            **household_data.model_dump()
        )
        db.add(household)
        await db.flush()
        
        # Add creator as admin member
        membership = HouseholdMembership(
            household_id=household.id,
            user_id=user_id,
            role="admin"
        )
        db.add(membership)
        
        # Update user's current household
        user = await UserService.get_user(db, user_id)
        if user:
            user.current_household_id = household.id
        
        # Grant access to user's shared recipes for the new household
        await HouseholdService._grant_user_recipes_to_household(db, user_id, household.id)
        
        await db.commit()
        await db.refresh(household)
        return household
    
    @staticmethod
    async def get_household(db: AsyncSession, household_id: uuid.UUID) -> Optional[Household]:
        """Get household by ID with members."""
        result = await db.execute(
            select(Household)
            .options(selectinload(Household.members).selectinload(HouseholdMembership.user))
            .where(Household.id == household_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_household_by_invite_code(db: AsyncSession, invite_code: str) -> Optional[Household]:
        """Get household by invite code."""
        result = await db.execute(
            select(Household).where(Household.invite_code == invite_code)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_household(db: AsyncSession, user_id: uuid.UUID) -> Optional[Household]:
        """Get the household that a user belongs to."""
        result = await db.execute(
            select(Household)
            .join(HouseholdMembership)
            .options(selectinload(Household.members).selectinload(HouseholdMembership.user))
            .where(HouseholdMembership.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_household(db: AsyncSession, household_id: uuid.UUID, household_data: HouseholdUpdate) -> Optional[Household]:
        """Update household."""
        household = await HouseholdService.get_household(db, household_id)
        if not household:
            return None
        
        for field, value in household_data.model_dump(exclude_unset=True).items():
            setattr(household, field, value)
        
        await db.commit()
        await db.refresh(household)
        return household
    
    @staticmethod
    async def join_household(db: AsyncSession, user_id: uuid.UUID, invite_code: str) -> Optional[HouseholdMembership]:
        """Join a household using invite code."""
        # Get household by invite code
        household = await HouseholdService.get_household_by_invite_code(db, invite_code)
        if not household:
            return None
        
        # Check if user is already in a household
        existing_membership = await db.execute(
            select(HouseholdMembership).where(HouseholdMembership.user_id == user_id)
        )
        if existing_membership.scalar_one_or_none():
            raise ValueError("User is already in a household")
        
        # Create membership
        membership = HouseholdMembership(
            household_id=household.id,
            user_id=user_id,
            role="member"
        )
        db.add(membership)
        
        # Update user's current household
        user = await UserService.get_user(db, user_id)
        if user:
            user.current_household_id = household.id
        
        # Grant access to user's shared recipes for the new household
        await HouseholdService._grant_user_recipes_to_household(db, user_id, household.id)
        
        await db.commit()
        await db.refresh(membership)
        return membership
    
    @staticmethod
    async def leave_household(db: AsyncSession, user_id: uuid.UUID) -> bool:
        """Remove user from their household."""
        # Get user's membership
        result = await db.execute(
            select(HouseholdMembership).where(HouseholdMembership.user_id == user_id)
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
            return False
        
        # Update user's current household
        user = await UserService.get_user(db, user_id)
        if user:
            user.current_household_id = None
        
        # Remove membership
        await db.delete(membership)
        await db.commit()
        return True
    
    @staticmethod
    async def update_member_role(db: AsyncSession, household_id: uuid.UUID, user_id: uuid.UUID, role: str) -> Optional[HouseholdMembership]:
        """Update a member's role in the household."""
        result = await db.execute(
            select(HouseholdMembership)
            .where(
                and_(
                    HouseholdMembership.household_id == household_id,
                    HouseholdMembership.user_id == user_id
                )
            )
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
            return None
        
        membership.role = role
        await db.commit()
        await db.refresh(membership)
        return membership
    
    @staticmethod
    async def remove_member(db: AsyncSession, household_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Remove a member from the household."""
        result = await db.execute(
            select(HouseholdMembership)
            .where(
                and_(
                    HouseholdMembership.household_id == household_id,
                    HouseholdMembership.user_id == user_id
                )
            )
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
            return False
        
        # Update user's current household if they're being removed
        user = await UserService.get_user(db, user_id)
        if user and user.current_household_id == household_id:
            user.current_household_id = None
        
        await db.delete(membership)
        await db.commit()
        return True
    
    @staticmethod
    async def get_household_members(db: AsyncSession, household_id: uuid.UUID) -> List[uuid.UUID]:
        """Get list of user IDs who are members of the household."""
        result = await db.execute(
            select(HouseholdMembership.user_id)
            .where(HouseholdMembership.household_id == household_id)
        )
        return result.scalars().all()

    @staticmethod
    async def _grant_user_recipes_to_household(db: AsyncSession, user_id: uuid.UUID, household_id: uuid.UUID) -> None:
        """Helper method to grant access to user's shared recipes for a household."""
        # Get all recipes shared by the user
        user_shared_recipes = await db.execute(
            select(Recipe.id)
            .where(
                and_(
                    Recipe.user_id == user_id,
                    Recipe.shared_with_household == True
                )
            )
        )
        
        # Grant household access for each shared recipe
        for recipe_id in user_shared_recipes.scalars():
            await RecipeService.grant_household_access(db, recipe_id, household_id, user_id)


class IngredientService:
    """Service for ingredient operations."""
    
    @staticmethod
    async def create_ingredient(db: AsyncSession, ingredient_data: IngredientCreate) -> Ingredient:
        """Create a new ingredient."""
        ingredient = Ingredient(**ingredient_data.model_dump())
        db.add(ingredient)
        await db.commit()
        await db.refresh(ingredient)
        return ingredient
    
    @staticmethod
    async def get_ingredient(db: AsyncSession, ingredient_id: uuid.UUID) -> Optional[Ingredient]:
        """Get ingredient by ID."""
        result = await db.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_ingredient_by_name(db: AsyncSession, name: str) -> Optional[Ingredient]:
        """Get ingredient by name."""
        result = await db.execute(select(Ingredient).where(Ingredient.name == name))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def search_ingredients(db: AsyncSession, query: str, limit: int = 20) -> List[Ingredient]:
        """Search ingredients by name."""
        result = await db.execute(
            select(Ingredient)
            .where(Ingredient.name.ilike(f"%{query}%"))
            .limit(limit)
        )
        return result.scalars().all()


class RecipeService:
    """Service for recipe operations."""
    
    @staticmethod
    async def create_recipe(db: AsyncSession, user_id: uuid.UUID, recipe_data: RecipeCreate) -> Recipe:
        """Create a new recipe with ingredients."""
        recipe_dict = recipe_data.model_dump(exclude={"ingredients"})
        recipe = Recipe(user_id=user_id, **recipe_dict)
        db.add(recipe)
        await db.flush()  # Get recipe ID
        
        # Add ingredients if provided
        if recipe_data.ingredients:
            for ingredient_data in recipe_data.ingredients:
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    **ingredient_data.model_dump()
                )
                db.add(recipe_ingredient)
        
        await db.commit()
        await db.refresh(recipe)
        return recipe
    
    @staticmethod
    async def create_recipe_from_scraped_data(db: AsyncSession, user_id: uuid.UUID, scraped_data: dict) -> Recipe:
        """Create a recipe from scraped data with ingredient parsing."""
        # Parse ingredients from scraped data
        ingredient_texts = scraped_data.get('ingredients', [])
        parsed_ingredients = IngredientParsingService.parse_ingredients_batch(ingredient_texts)
        
        # Create recipe with scraped data
        recipe = Recipe(
            user_id=user_id,
            title=scraped_data.get('title', ''),
            description=scraped_data.get('description', ''),
            instructions=scraped_data.get('instructions', '').split('\n') if scraped_data.get('instructions') else [],
            prep_time=scraped_data.get('prep_time'),
            cook_time=scraped_data.get('cook_time'),
            total_time=scraped_data.get('total_time'),
            servings=RecipeService._parse_servings(scraped_data.get('yields', '')),
            source_url=scraped_data.get('canonical_url', ''),
            image_url=scraped_data.get('image', ''),
            source_type='scraped',
            author=scraped_data.get('author', ''),
            cuisine=scraped_data.get('cuisine', '') if scraped_data.get('cuisine') != 'Error: recipe-scrapers exception: No cuisine data in SchemaOrg.' else None,
            category=scraped_data.get('category', ''),
            keywords=scraped_data.get('keywords', []),
            site_name=scraped_data.get('site_name', ''),
            language=scraped_data.get('language', '')
        )
        db.add(recipe)
        await db.flush()
        
        # Add parsed ingredients
        for i, parsed_ingredient in enumerate(parsed_ingredients):
            # Find or create ingredient
            ingredient = None
            if parsed_ingredient.get('ingredient_name'):
                ingredient = await IngredientParsingService.find_or_create_ingredient(
                    db, parsed_ingredient['ingredient_name']
                )
            
            # Create recipe ingredient
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id if ingredient else None,
                quantity=parsed_ingredient.get('quantity'),
                unit=parsed_ingredient.get('unit'),
                notes=parsed_ingredient.get('notes'),
                order_index=i,
                raw_ingredient_text=parsed_ingredient.get('raw_text'),
                parsing_confidence=parsed_ingredient.get('parsing_confidence')
            )
            db.add(recipe_ingredient)
        
        # Add nutrition data if available
        nutrients = scraped_data.get('nutrients', {})
        if nutrients:
            nutrition = RecipeNutrition(
                recipe_id=recipe.id,
                calories=RecipeService._parse_numeric_value(nutrients.get('calories')),
                protein_grams=RecipeService._parse_numeric_value(nutrients.get('proteinContent')),
                carbs_grams=RecipeService._parse_numeric_value(nutrients.get('carbohydrateContent')),
                fat_grams=RecipeService._parse_numeric_value(nutrients.get('fatContent')),
                fiber_grams=RecipeService._parse_numeric_value(nutrients.get('fiberContent')),
                sugar_grams=RecipeService._parse_numeric_value(nutrients.get('sugarContent')),
                sodium_mg=RecipeService._parse_numeric_value(nutrients.get('sodiumContent')),
                saturated_fat_grams=RecipeService._parse_numeric_value(nutrients.get('saturatedFatContent')),
                unsaturated_fat_grams=RecipeService._parse_numeric_value(nutrients.get('unsaturatedFatContent')),
                trans_fat_grams=RecipeService._parse_numeric_value(nutrients.get('transFatContent'))
            )
            db.add(nutrition)
        
        await db.commit()
        await db.refresh(recipe)
        return recipe
    
    @staticmethod
    def _parse_servings(yields_text: str) -> Optional[int]:
        """Parse servings from yields text like '4 servings' or '8 servings'."""
        if not yields_text:
            return None
        
        import re
        match = re.search(r'(\d+)', yields_text)
        return int(match.group(1)) if match else None
    
    @staticmethod
    def _parse_numeric_value(value: str) -> Optional[float]:
        """Parse numeric value from text like '256 calories' or '19 grams'."""
        if not value:
            return None
        
        import re
        match = re.search(r'([0-9.]+)', str(value))
        try:
            return float(match.group(1)) if match else None
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    async def get_recipe(db: AsyncSession, recipe_id: uuid.UUID) -> Optional[Recipe]:
        """Get recipe by ID with ingredients."""
        result = await db.execute(
            select(Recipe)
            .options(selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient))
            .where(Recipe.id == recipe_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_recipes(db: AsyncSession, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[Recipe]:
        """Get recipes for a user (their own recipes only)."""
        result = await db.execute(
            select(Recipe)
            .where(Recipe.user_id == user_id)
            .order_by(Recipe.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_accessible_recipes(db: AsyncSession, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[dict]:
        """Get all recipes accessible to a user with access level information."""
        # Get user's household
        user_household = await HouseholdService.get_user_household(db, user_id)
        
        if not user_household:
            # No household - return only user's recipes with full access
            recipes = await RecipeService.get_user_recipes(db, user_id, limit, offset)
            return [{"recipe": recipe, "can_edit": True, "access_type": "owner"} for recipe in recipes]
        
        # Query for recipes accessible through household access grants
        result = await db.execute(
            select(Recipe)
            .outerjoin(RecipeHouseholdAccess, Recipe.id == RecipeHouseholdAccess.recipe_id)
            .join(HouseholdMembership, RecipeHouseholdAccess.household_id == HouseholdMembership.household_id)
            .where(
                or_(
                    Recipe.user_id == user_id,  # User's own recipes
                    HouseholdMembership.user_id == user_id  # Recipes accessible to user's household
                )
            )
            .order_by(Recipe.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        recipes_with_access = []
        for recipe in result.scalars():
            if recipe.user_id == user_id:
                # User owns the recipe
                recipes_with_access.append({
                    "recipe": recipe,
                    "can_edit": True,
                    "access_type": "owner"
                })
            else:
                # User has access through household
                recipes_with_access.append({
                    "recipe": recipe,
                    "can_edit": False,
                    "access_type": "household_shared"
                })
        
        return recipes_with_access

    @staticmethod
    async def get_household_recipes(db: AsyncSession, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[Recipe]:
        """Get all recipes accessible to a user (backward compatibility method)."""
        accessible_recipes = await RecipeService.get_accessible_recipes(db, user_id, limit, offset)
        return [item["recipe"] for item in accessible_recipes]
    
    @staticmethod
    async def update_recipe(db: AsyncSession, recipe_id: uuid.UUID, recipe_data: RecipeUpdate) -> Optional[Recipe]:
        """Update recipe."""
        recipe = await RecipeService.get_recipe(db, recipe_id)
        if not recipe:
            return None
        
        for field, value in recipe_data.model_dump(exclude_unset=True).items():
            setattr(recipe, field, value)
        
        await db.commit()
        await db.refresh(recipe)
        return recipe
    
    @staticmethod
    async def delete_recipe(db: AsyncSession, recipe_id: uuid.UUID) -> bool:
        """Delete recipe."""
        recipe = await RecipeService.get_recipe(db, recipe_id)
        if not recipe:
            return False
        
        await db.delete(recipe)
        await db.commit()
        return True

    @staticmethod
    async def grant_household_access(db: AsyncSession, recipe_id: uuid.UUID, household_id: uuid.UUID, granted_by: uuid.UUID) -> Optional[RecipeHouseholdAccess]:
        """Grant access to a recipe for a household."""
        # Check if access already exists
        existing_access = await db.execute(
            select(RecipeHouseholdAccess)
            .where(
                and_(
                    RecipeHouseholdAccess.recipe_id == recipe_id,
                    RecipeHouseholdAccess.household_id == household_id
                )
            )
        )
        if existing_access.scalar_one_or_none():
            return None  # Access already exists
        
        # Create new access grant
        access_grant = RecipeHouseholdAccess(
            recipe_id=recipe_id,
            household_id=household_id,
            granted_by=granted_by
        )
        db.add(access_grant)
        await db.commit()
        await db.refresh(access_grant)
        return access_grant

    @staticmethod
    async def revoke_household_access(db: AsyncSession, recipe_id: uuid.UUID, household_id: uuid.UUID) -> bool:
        """Revoke access to a recipe for a household."""
        result = await db.execute(
            select(RecipeHouseholdAccess)
            .where(
                and_(
                    RecipeHouseholdAccess.recipe_id == recipe_id,
                    RecipeHouseholdAccess.household_id == household_id
                )
            )
        )
        access_grant = result.scalar_one_or_none()
        
        if not access_grant:
            return False
        
        await db.delete(access_grant)
        await db.commit()
        return True

    @staticmethod
    async def copy_recipe(db: AsyncSession, recipe_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Recipe]:
        """Copy a recipe for a user (creates a new recipe with same content but new ownership)."""
        # Get the original recipe with ingredients
        original_recipe = await RecipeService.get_recipe(db, recipe_id)
        if not original_recipe:
            return None
        
        # Create new recipe with copied data
        new_recipe_data = {
            "title": f"{original_recipe.title} (Copy)",
            "description": original_recipe.description,
            "instructions": original_recipe.instructions,
            "prep_time": original_recipe.prep_time,
            "cook_time": original_recipe.cook_time,
            "servings": original_recipe.servings,
            "source_url": original_recipe.source_url,
            "image_url": original_recipe.image_url,
            "difficulty_level": original_recipe.difficulty_level,
            "source_type": "manual",  # Copied recipes are manual
            "shared_with_household": True  # Default to sharing
        }
        
        # Remove None values
        new_recipe_data = {k: v for k, v in new_recipe_data.items() if v is not None}
        
        new_recipe = Recipe(user_id=user_id, **new_recipe_data)
        db.add(new_recipe)
        await db.flush()  # Get new recipe ID
        
        # Copy ingredients
        for orig_ingredient in original_recipe.recipe_ingredients:
            new_ingredient = RecipeIngredient(
                recipe_id=new_recipe.id,
                ingredient_id=orig_ingredient.ingredient_id,
                quantity=orig_ingredient.quantity,
                unit=orig_ingredient.unit,
                notes=orig_ingredient.notes,
                order_index=orig_ingredient.order_index,
                raw_ingredient_text=getattr(orig_ingredient, 'raw_ingredient_text', None),
                parsing_confidence=getattr(orig_ingredient, 'parsing_confidence', None)
            )
            db.add(new_ingredient)
        
        await db.commit()
        await db.refresh(new_recipe)
        return new_recipe

    @staticmethod
    async def can_user_edit_recipe(db: AsyncSession, recipe_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if a user can edit a recipe (must be the owner)."""
        recipe = await db.execute(
            select(Recipe.user_id)
            .where(Recipe.id == recipe_id)
        )
        recipe_owner = recipe.scalar_one_or_none()
        return recipe_owner == user_id

    @staticmethod
    async def can_user_access_recipe(db: AsyncSession, recipe_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if a user can access a recipe (owns it or has household access)."""
        # Check if user owns the recipe
        recipe = await db.execute(
            select(Recipe.user_id)
            .where(Recipe.id == recipe_id)
        )
        recipe_owner = recipe.scalar_one_or_none()
        
        if recipe_owner == user_id:
            return True
        
        # Check if user has household access
        user_household = await HouseholdService.get_user_household(db, user_id)
        if not user_household:
            return False
        
        access_check = await db.execute(
            select(RecipeHouseholdAccess)
            .where(
                and_(
                    RecipeHouseholdAccess.recipe_id == recipe_id,
                    RecipeHouseholdAccess.household_id == user_household.id
                )
            )
        )
        
        return access_check.scalar_one_or_none() is not None


class MealPlanService:
    """Service for meal plan operations."""
    
    @staticmethod
    async def create_meal_plan(db: AsyncSession, user_id: uuid.UUID, meal_plan_data: MealPlanCreate) -> MealPlan:
        """Create a new meal plan."""
        # Get user's household
        user_household = await HouseholdService.get_user_household(db, user_id)
        if not user_household:
            raise ValueError("User must be in a household to create meal plans")
        
        meal_plan = MealPlan(
            user_id=user_id, 
            household_id=user_household.id,
            **meal_plan_data.model_dump()
        )
        db.add(meal_plan)
        await db.commit()
        await db.refresh(meal_plan)
        return meal_plan
    
    @staticmethod
    async def get_meal_plan(db: AsyncSession, meal_plan_id: uuid.UUID) -> Optional[MealPlan]:
        """Get meal plan by ID with planned meals."""
        result = await db.execute(
            select(MealPlan)
            .options(selectinload(MealPlan.planned_meals).selectinload(PlannedMeal.recipe))
            .where(MealPlan.id == meal_plan_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_meal_plans(db: AsyncSession, user_id: uuid.UUID) -> List[MealPlan]:
        """Get meal plans for a user's household."""
        # Get user's household
        user_household = await HouseholdService.get_user_household(db, user_id)
        if not user_household:
            return []
        
        result = await db.execute(
            select(MealPlan)
            .where(MealPlan.household_id == user_household.id)
            .order_by(MealPlan.week_start.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def add_planned_meal(db: AsyncSession, meal_plan_id: uuid.UUID, planned_meal_data: PlannedMealCreate) -> PlannedMeal:
        """Add a planned meal to a meal plan."""
        planned_meal = PlannedMeal(meal_plan_id=meal_plan_id, **planned_meal_data.model_dump())
        db.add(planned_meal)
        await db.commit()
        await db.refresh(planned_meal)
        return planned_meal
    
    @staticmethod
    async def update_planned_meal(db: AsyncSession, planned_meal_id: uuid.UUID, planned_meal_data: PlannedMealUpdate) -> Optional[PlannedMeal]:
        """Update a planned meal."""
        result = await db.execute(select(PlannedMeal).where(PlannedMeal.id == planned_meal_id))
        planned_meal = result.scalar_one_or_none()
        
        if not planned_meal:
            return None
        
        for field, value in planned_meal_data.model_dump(exclude_unset=True).items():
            setattr(planned_meal, field, value)
        
        await db.commit()
        await db.refresh(planned_meal)
        return planned_meal


class ShoppingListService:
    """Service for shopping list operations."""
    
    @staticmethod
    async def create_shopping_list(db: AsyncSession, user_id: uuid.UUID, shopping_list_data: ShoppingListCreate) -> ShoppingList:
        """Create a new shopping list."""
        # Get user's household
        user_household = await HouseholdService.get_user_household(db, user_id)
        if not user_household:
            raise ValueError("User must be in a household to create shopping lists")
            
        shopping_list = ShoppingList(
            user_id=user_id, 
            household_id=user_household.id,
            **shopping_list_data.model_dump()
        )
        db.add(shopping_list)
        await db.commit()
        await db.refresh(shopping_list)
        return shopping_list
    
    @staticmethod
    async def get_shopping_list(db: AsyncSession, shopping_list_id: uuid.UUID) -> Optional[ShoppingList]:
        """Get shopping list by ID with items."""
        result = await db.execute(
            select(ShoppingList)
            .options(selectinload(ShoppingList.shopping_list_items).selectinload(ShoppingListItem.ingredient))
            .where(ShoppingList.id == shopping_list_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_shopping_lists(db: AsyncSession, user_id: uuid.UUID) -> List[ShoppingList]:
        """Get shopping lists for a user's household."""
        # Get user's household
        user_household = await HouseholdService.get_user_household(db, user_id)
        if not user_household:
            return []
            
        result = await db.execute(
            select(ShoppingList)
            .where(ShoppingList.household_id == user_household.id)
            .order_by(ShoppingList.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def add_shopping_list_item(db: AsyncSession, shopping_list_id: uuid.UUID, item_data: ShoppingListItemCreate) -> ShoppingListItem:
        """Add item to shopping list."""
        item = ShoppingListItem(shopping_list_id=shopping_list_id, **item_data.model_dump())
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item
    
    @staticmethod
    async def update_shopping_list_item(db: AsyncSession, item_id: uuid.UUID, item_data: ShoppingListItemUpdate) -> Optional[ShoppingListItem]:
        """Update shopping list item."""
        result = await db.execute(select(ShoppingListItem).where(ShoppingListItem.id == item_id))
        item = result.scalar_one_or_none()
        
        if not item:
            return None
        
        for field, value in item_data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        
        await db.commit()
        await db.refresh(item)
        return item
    
    @staticmethod
    async def generate_shopping_list_from_meal_plan(db: AsyncSession, user_id: uuid.UUID, meal_plan_id: uuid.UUID) -> ShoppingList:
        """Generate shopping list from meal plan."""
        # Get meal plan with recipes
        meal_plan = await MealPlanService.get_meal_plan(db, meal_plan_id)
        if not meal_plan:
            raise ValueError("Meal plan not found")
        
        # Create shopping list
        shopping_list = ShoppingList(
            user_id=user_id,
            household_id=meal_plan.household_id,
            meal_plan_id=meal_plan_id,
            name=f"Shopping List for {meal_plan.name or 'Meal Plan'}"
        )
        db.add(shopping_list)
        await db.flush()
        
        # Aggregate ingredients from all planned meals
        ingredient_quantities = {}
        for planned_meal in meal_plan.planned_meals:
            if planned_meal.recipe and planned_meal.recipe.recipe_ingredients:
                for recipe_ingredient in planned_meal.recipe.recipe_ingredients:
                    ingredient_id = recipe_ingredient.ingredient_id
                    if ingredient_id not in ingredient_quantities:
                        ingredient_quantities[ingredient_id] = {
                            'quantity': recipe_ingredient.quantity or 0,
                            'unit': recipe_ingredient.unit,
                            'ingredient': recipe_ingredient.ingredient
                        }
                    else:
                        # Simple addition - could be enhanced with unit conversion
                        if recipe_ingredient.quantity:
                            ingredient_quantities[ingredient_id]['quantity'] += recipe_ingredient.quantity
        
        # Create shopping list items
        for ingredient_id, data in ingredient_quantities.items():
            item = ShoppingListItem(
                shopping_list_id=shopping_list.id,
                ingredient_id=ingredient_id,
                quantity=data['quantity'],
                unit=data['unit'],
                category=data['ingredient'].category if data['ingredient'] else None
            )
            db.add(item)
        
        await db.commit()
        await db.refresh(shopping_list)
        return shopping_list


class RecipeUsageService:
    """Service for recipe usage tracking."""
    
    @staticmethod
    async def record_usage(db: AsyncSession, user_id: uuid.UUID, usage_data: RecipeUsageCreate) -> RecipeUsage:
        """Record recipe usage."""
        usage = RecipeUsage(user_id=user_id, **usage_data.model_dump())
        db.add(usage)
        await db.commit()
        await db.refresh(usage)
        return usage
    
    @staticmethod
    async def get_recipe_usage_stats(db: AsyncSession, recipe_id: uuid.UUID) -> dict:
        """Get usage statistics for a recipe."""
        result = await db.execute(
            select(RecipeUsage)
            .where(RecipeUsage.recipe_id == recipe_id)
        )
        usages = result.scalars().all()
        
        if not usages:
            return {"usage_count": 0, "average_rating": None, "average_cooking_time": None}
        
        total_usages = len(usages)
        ratings = [u.rating for u in usages if u.rating]
        cooking_times = [u.cooking_time_actual for u in usages if u.cooking_time_actual]
        
        return {
            "usage_count": total_usages,
            "average_rating": sum(ratings) / len(ratings) if ratings else None,
            "average_cooking_time": sum(cooking_times) / len(cooking_times) if cooking_times else None
        }
    
    @staticmethod
    async def get_user_recipe_usage(db: AsyncSession, user_id: uuid.UUID, limit: int = 10) -> List[RecipeUsage]:
        """Get recent recipe usage for a user."""
        result = await db.execute(
            select(RecipeUsage)
            .where(RecipeUsage.user_id == user_id)
            .order_by(RecipeUsage.used_at.desc())
            .limit(limit)
        )
        return result.scalars().all()