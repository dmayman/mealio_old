"""Enhanced SQLAlchemy models with new nutrition and equipment tables."""

from sqlalchemy import Column, String, Integer, Text, DECIMAL, Boolean, DateTime, Date, ForeignKey, ARRAY, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class RecipeNutrition(Base):
    """Recipe nutrition information."""
    __tablename__ = "recipe_nutrition"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, unique=True)
    calories = Column(DECIMAL(8, 2))
    protein_grams = Column(DECIMAL(8, 2))
    carbs_grams = Column(DECIMAL(8, 2))
    fat_grams = Column(DECIMAL(8, 2))
    fiber_grams = Column(DECIMAL(8, 2))
    sugar_grams = Column(DECIMAL(8, 2))
    sodium_mg = Column(DECIMAL(10, 2))
    saturated_fat_grams = Column(DECIMAL(8, 2))
    unsaturated_fat_grams = Column(DECIMAL(8, 2))
    trans_fat_grams = Column(DECIMAL(8, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    recipe = relationship("Recipe", back_populates="nutrition")


class RecipeEquipment(Base):
    """Recipe equipment/tools."""
    __tablename__ = "recipe_equipment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    equipment_name = Column(String(255), nullable=False)
    is_required = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)

    # Relationships
    recipe = relationship("Recipe", back_populates="equipment")