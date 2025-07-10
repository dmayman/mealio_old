-- Enhanced ingredient parsing fields
-- Adds support for parsed ingredient data with separate quantity/unit fields

-- Add new columns to recipe_ingredients table
ALTER TABLE recipe_ingredients 
ADD COLUMN IF NOT EXISTS quantity_display TEXT, -- Combined text for UI (e.g., "2 tablespoons")
ADD COLUMN IF NOT EXISTS quantity_value DECIMAL(10,3), -- Numeric value for scaling (e.g., 2.0)
ADD COLUMN IF NOT EXISTS unit_standardized VARCHAR(50), -- Standardized unit for scaling (e.g., "tablespoon")
ADD COLUMN IF NOT EXISTS ingredient_text TEXT, -- Clean ingredient text without quantity/notes
ADD COLUMN IF NOT EXISTS ingredient_notes TEXT, -- Preparation notes (e.g., "shredded", "patted dry")
ADD COLUMN IF NOT EXISTS raw_ingredient_text TEXT; -- Original scraped string

-- Add comments to explain the new fields
COMMENT ON COLUMN recipe_ingredients.quantity_display IS 'Display-formatted quantity with unit (e.g., "2 tablespoons", "1/4 cup")';
COMMENT ON COLUMN recipe_ingredients.quantity_value IS 'Numeric quantity value for recipe scaling calculations';
COMMENT ON COLUMN recipe_ingredients.unit_standardized IS 'Standardized singular unit name for programmatic use';
COMMENT ON COLUMN recipe_ingredients.ingredient_text IS 'Clean ingredient name with quantity and notes removed';
COMMENT ON COLUMN recipe_ingredients.ingredient_notes IS 'Preparation instructions and notes (e.g., "shredded", "patted dry", "finely chopped")';

-- Add index for better query performance on quantity values (useful for scaling)
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_quantity_value ON recipe_ingredients(quantity_value);
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_unit ON recipe_ingredients(unit_standardized);