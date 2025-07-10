-- Enhanced Recipe Schema to Handle All Scraped Data
-- This extends the current schema to capture all recipe-scrapers fields

-- Add missing columns to recipes table
ALTER TABLE recipes ADD COLUMN total_time INTEGER; -- total time in minutes
ALTER TABLE recipes ADD COLUMN author VARCHAR(255); -- recipe author
ALTER TABLE recipes ADD COLUMN cuisine VARCHAR(100); -- cuisine type
ALTER TABLE recipes ADD COLUMN category VARCHAR(255); -- meal category 
ALTER TABLE recipes ADD COLUMN keywords TEXT[]; -- array of keywords/tags
ALTER TABLE recipes ADD COLUMN site_name VARCHAR(255); -- source site name
ALTER TABLE recipes ADD COLUMN language VARCHAR(10); -- recipe language (en, es, etc.)

-- Create nutrition table for detailed nutrition info
CREATE TABLE recipe_nutrition (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE UNIQUE,
  calories DECIMAL(8,2),
  protein_grams DECIMAL(8,2),
  carbs_grams DECIMAL(8,2),
  fat_grams DECIMAL(8,2),
  fiber_grams DECIMAL(8,2),
  sugar_grams DECIMAL(8,2),
  sodium_mg DECIMAL(10,2),
  saturated_fat_grams DECIMAL(8,2),
  unsaturated_fat_grams DECIMAL(8,2),
  trans_fat_grams DECIMAL(8,2),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create equipment table for recipe equipment/tools
CREATE TABLE recipe_equipment (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,
  equipment_name VARCHAR(255) NOT NULL,
  is_required BOOLEAN DEFAULT TRUE,
  order_index INTEGER DEFAULT 0
);

-- Enhance recipe_ingredients to store raw scraped text as backup
ALTER TABLE recipe_ingredients ADD COLUMN raw_ingredient_text TEXT; -- original scraped string
ALTER TABLE recipe_ingredients ADD COLUMN parsing_confidence DECIMAL(3,2); -- confidence score 0-1

-- Add indexes for new fields
CREATE INDEX idx_recipes_author ON recipes(author);
CREATE INDEX idx_recipes_cuisine ON recipes(cuisine);
CREATE INDEX idx_recipes_category ON recipes(category);
CREATE INDEX idx_recipes_total_time ON recipes(total_time);
CREATE INDEX idx_recipe_nutrition_recipe_id ON recipe_nutrition(recipe_id);
CREATE INDEX idx_recipe_equipment_recipe_id ON recipe_equipment(recipe_id);

-- Add GIN index for keywords array
CREATE INDEX idx_recipes_keywords ON recipes USING gin(keywords);