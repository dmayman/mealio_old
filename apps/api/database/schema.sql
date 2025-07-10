-- Mealio Complete Database Schema
-- Fresh installation with households feature included

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User profiles table (extends Supabase Auth users)
-- The auth.users table is managed by Supabase Auth
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name VARCHAR(255),
  current_household_id UUID, -- Will be set after households table is created
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Households table
CREATE TABLE households (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  created_by UUID REFERENCES auth.users(id),
  invite_code VARCHAR(50) UNIQUE, -- for easy household joining
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Household memberships table  
CREATE TABLE household_memberships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  household_id UUID REFERENCES households(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  role VARCHAR(20) DEFAULT 'member' CHECK (role IN ('admin', 'member')),
  joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id) -- Users can only be in one household
);

-- Add foreign key constraint for user_profiles.current_household_id after households table exists
ALTER TABLE user_profiles ADD CONSTRAINT fk_user_profiles_current_household 
  FOREIGN KEY (current_household_id) REFERENCES households(id);

-- Ingredients master table
CREATE TABLE ingredients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) UNIQUE NOT NULL,
  category VARCHAR(100), -- vegetables, proteins, dairy, etc.
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recipes table
CREATE TABLE recipes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  instructions TEXT[], -- Array of instruction steps
  prep_time INTEGER, -- minutes
  cook_time INTEGER, -- minutes
  total_time INTEGER, -- total time in minutes
  servings INTEGER,
  source_url VARCHAR(500),
  image_url VARCHAR(500),
  difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
  source_type VARCHAR(20) DEFAULT 'manual' CHECK (source_type IN ('scraped', 'manual', 'generated')),
  shared_with_household BOOLEAN DEFAULT TRUE, -- whether recipe is shared with household members
  author VARCHAR(255), -- recipe author
  cuisine VARCHAR(100), -- cuisine type
  category VARCHAR(255), -- meal category
  keywords TEXT[], -- array of keywords/tags
  site_name VARCHAR(255), -- source site name
  language VARCHAR(10), -- recipe language (en, es, etc.)
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recipe ingredients junction table
CREATE TABLE recipe_ingredients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,
  ingredient_id UUID REFERENCES ingredients(id),
  quantity DECIMAL(10,2),
  unit VARCHAR(50), -- cups, tbsp, lbs, etc.
  notes TEXT, -- "finely chopped", "to taste", etc.
  order_index INTEGER DEFAULT 0, -- for maintaining ingredient order
  raw_ingredient_text TEXT, -- original scraped string
  parsing_confidence DECIMAL(3,2) -- confidence score 0-1
);

-- Meal plans table
CREATE TABLE meal_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE, -- creator of the meal plan
  household_id UUID REFERENCES households(id) ON DELETE CASCADE, -- household this meal plan belongs to
  week_start DATE NOT NULL,
  name VARCHAR(255), -- "Week of Jan 15", "Meal Prep Week", etc.
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Planned meals table
CREATE TABLE planned_meals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  meal_plan_id UUID REFERENCES meal_plans(id) ON DELETE CASCADE,
  recipe_id UUID REFERENCES recipes(id),
  planned_date DATE,
  meal_type VARCHAR(50) CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
  completed BOOLEAN DEFAULT FALSE,
  notes TEXT, -- user notes for this specific meal
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Shopping lists table
CREATE TABLE shopping_lists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  meal_plan_id UUID REFERENCES meal_plans(id),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE, -- creator of the shopping list
  household_id UUID REFERENCES households(id) ON DELETE CASCADE, -- household this shopping list belongs to
  name VARCHAR(255) DEFAULT 'Shopping List',
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'archived')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Shopping list items table
CREATE TABLE shopping_list_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  shopping_list_id UUID REFERENCES shopping_lists(id) ON DELETE CASCADE,
  ingredient_id UUID REFERENCES ingredients(id),
  quantity DECIMAL(10,2),
  unit VARCHAR(50),
  checked BOOLEAN DEFAULT FALSE,
  category VARCHAR(100), -- produce, dairy, meat, etc. (for store organization)
  notes TEXT,
  order_index INTEGER DEFAULT 0 -- for maintaining shopping order
);

-- Recipe usage tracking
CREATE TABLE recipe_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,
  used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  notes TEXT, -- cooking notes, modifications made, etc.
  cooking_time_actual INTEGER -- actual time taken to cook
);

-- Essential indexes for performance
-- User and household indexes
CREATE INDEX idx_user_profiles_household_id ON user_profiles(current_household_id);
CREATE INDEX idx_households_created_by ON households(created_by);
CREATE INDEX idx_households_invite_code ON households(invite_code);
CREATE INDEX idx_household_memberships_household_id ON household_memberships(household_id);
CREATE INDEX idx_household_memberships_user_id ON household_memberships(user_id);

-- Recipe indexes
CREATE INDEX idx_recipes_user_id ON recipes(user_id);
CREATE INDEX idx_recipes_created_at ON recipes(created_at DESC);
CREATE INDEX idx_recipes_user_created ON recipes(user_id, created_at DESC);
CREATE INDEX idx_recipes_shared_household ON recipes(shared_with_household);

CREATE INDEX idx_recipe_ingredients_recipe_id ON recipe_ingredients(recipe_id);
CREATE INDEX idx_recipe_ingredients_ingredient_id ON recipe_ingredients(ingredient_id);

-- Meal plan indexes
CREATE INDEX idx_meal_plans_user_id ON meal_plans(user_id);
CREATE INDEX idx_meal_plans_household_id ON meal_plans(household_id);
CREATE INDEX idx_meal_plans_week_start ON meal_plans(week_start DESC);
CREATE INDEX idx_meal_plans_household_week ON meal_plans(household_id, week_start DESC);

CREATE INDEX idx_planned_meals_meal_plan_id ON planned_meals(meal_plan_id);
CREATE INDEX idx_planned_meals_date ON planned_meals(planned_date);

-- Shopping list indexes
CREATE INDEX idx_shopping_lists_user_id ON shopping_lists(user_id);
CREATE INDEX idx_shopping_lists_household_id ON shopping_lists(household_id);
CREATE INDEX idx_shopping_lists_meal_plan_id ON shopping_lists(meal_plan_id);

CREATE INDEX idx_shopping_list_items_list_id ON shopping_list_items(shopping_list_id);

-- Recipe usage indexes
CREATE INDEX idx_recipe_usage_user_id ON recipe_usage(user_id);
CREATE INDEX idx_recipe_usage_recipe_id ON recipe_usage(recipe_id);
CREATE INDEX idx_recipe_usage_used_at ON recipe_usage(used_at DESC);

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

-- Add indexes for new recipe fields
CREATE INDEX idx_recipes_author ON recipes(author);
CREATE INDEX idx_recipes_cuisine ON recipes(cuisine);
CREATE INDEX idx_recipes_category ON recipes(category);
CREATE INDEX idx_recipes_total_time ON recipes(total_time);
CREATE INDEX idx_recipe_nutrition_recipe_id ON recipe_nutrition(recipe_id);
CREATE INDEX idx_recipe_equipment_recipe_id ON recipe_equipment(recipe_id);

-- Add GIN index for keywords array
CREATE INDEX idx_recipes_keywords ON recipes USING gin(keywords);

-- Full-text search index for recipes
CREATE INDEX idx_recipes_title_search ON recipes USING gin(to_tsvector('english', title));
CREATE INDEX idx_ingredients_name_search ON ingredients USING gin(to_tsvector('english', name));

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recipes_updated_at BEFORE UPDATE ON recipes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meal_plans_updated_at BEFORE UPDATE ON meal_plans 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shopping_lists_updated_at BEFORE UPDATE ON shopping_lists 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_households_updated_at BEFORE UPDATE ON households 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to handle new user profile creation
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO user_profiles (id, display_name)
  VALUES (NEW.id, NEW.raw_user_meta_data->>'display_name');
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically create user profile when auth user is created
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Row Level Security (RLS) Policies
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE households ENABLE ROW LEVEL SECURITY;
ALTER TABLE household_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipe_ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE meal_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE planned_meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopping_lists ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopping_list_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipe_usage ENABLE ROW LEVEL SECURITY;

-- User profiles: users can only see/edit their own profile
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);

-- Households: users can see households they belong to
CREATE POLICY "Users can view their household" ON households FOR SELECT 
USING (
  EXISTS (
    SELECT 1 FROM household_memberships 
    WHERE household_memberships.household_id = households.id 
    AND household_memberships.user_id = auth.uid()
  )
);

CREATE POLICY "Users can create households" ON households FOR INSERT 
WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Household admins can update household" ON households FOR UPDATE 
USING (
  EXISTS (
    SELECT 1 FROM household_memberships 
    WHERE household_memberships.household_id = households.id 
    AND household_memberships.user_id = auth.uid() 
    AND household_memberships.role = 'admin'
  )
);

-- Household memberships: users can see memberships for their household
CREATE POLICY "Users can view household memberships" ON household_memberships FOR SELECT 
USING (
  user_id = auth.uid() OR 
  EXISTS (
    SELECT 1 FROM household_memberships hm 
    WHERE hm.household_id = household_memberships.household_id 
    AND hm.user_id = auth.uid()
  )
);

CREATE POLICY "Users can join households" ON household_memberships FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Admins can manage memberships" ON household_memberships FOR ALL 
USING (
  EXISTS (
    SELECT 1 FROM household_memberships hm 
    WHERE hm.household_id = household_memberships.household_id 
    AND hm.user_id = auth.uid() 
    AND hm.role = 'admin'
  )
);

-- Recipes: users can see their own recipes + shared household recipes
CREATE POLICY "Users can view accessible recipes" ON recipes FOR SELECT 
USING (
  user_id = auth.uid() OR 
  (shared_with_household = true AND EXISTS (
    SELECT 1 FROM household_memberships hm1, household_memberships hm2 
    WHERE hm1.user_id = recipes.user_id 
    AND hm2.user_id = auth.uid() 
    AND hm1.household_id = hm2.household_id
  ))
);

CREATE POLICY "Users can create recipes" ON recipes FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own recipes" ON recipes FOR UPDATE 
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own recipes" ON recipes FOR DELETE 
USING (auth.uid() = user_id);

-- Recipe ingredients: follow recipe permissions
CREATE POLICY "Users can view recipe ingredients" ON recipe_ingredients FOR SELECT 
USING (
  EXISTS (
    SELECT 1 FROM recipes 
    WHERE recipes.id = recipe_ingredients.recipe_id 
    AND (
      recipes.user_id = auth.uid() OR 
      (recipes.shared_with_household = true AND EXISTS (
        SELECT 1 FROM household_memberships hm1, household_memberships hm2 
        WHERE hm1.user_id = recipes.user_id 
        AND hm2.user_id = auth.uid() 
        AND hm1.household_id = hm2.household_id
      ))
    )
  )
);

CREATE POLICY "Users can manage own recipe ingredients" ON recipe_ingredients FOR ALL 
USING (
  EXISTS (
    SELECT 1 FROM recipes 
    WHERE recipes.id = recipe_ingredients.recipe_id 
    AND recipes.user_id = auth.uid()
  )
);

-- Meal plans: household members can see household meal plans
CREATE POLICY "Users can view household meal plans" ON meal_plans FOR SELECT 
USING (
  EXISTS (
    SELECT 1 FROM household_memberships 
    WHERE household_memberships.household_id = meal_plans.household_id 
    AND household_memberships.user_id = auth.uid()
  )
);

CREATE POLICY "Household members can create meal plans" ON meal_plans FOR INSERT 
WITH CHECK (
  auth.uid() = user_id AND 
  EXISTS (
    SELECT 1 FROM household_memberships 
    WHERE household_memberships.household_id = meal_plans.household_id 
    AND household_memberships.user_id = auth.uid()
  )
);

CREATE POLICY "Household members can update meal plans" ON meal_plans FOR UPDATE 
USING (
  EXISTS (
    SELECT 1 FROM household_memberships 
    WHERE household_memberships.household_id = meal_plans.household_id 
    AND household_memberships.user_id = auth.uid()
  )
);

-- Shopping lists: household members can see household shopping lists
CREATE POLICY "Users can view household shopping lists" ON shopping_lists FOR SELECT 
USING (
  EXISTS (
    SELECT 1 FROM household_memberships 
    WHERE household_memberships.household_id = shopping_lists.household_id 
    AND household_memberships.user_id = auth.uid()
  )
);

CREATE POLICY "Household members can create shopping lists" ON shopping_lists FOR INSERT 
WITH CHECK (
  auth.uid() = user_id AND 
  EXISTS (
    SELECT 1 FROM household_memberships 
    WHERE household_memberships.household_id = shopping_lists.household_id 
    AND household_memberships.user_id = auth.uid()
  )
);

CREATE POLICY "Household members can update shopping lists" ON shopping_lists FOR UPDATE 
USING (
  EXISTS (
    SELECT 1 FROM household_memberships 
    WHERE household_memberships.household_id = shopping_lists.household_id 
    AND household_memberships.user_id = auth.uid()
  )
);

-- Shopping list items: follow shopping list permissions
CREATE POLICY "Users can view shopping list items" ON shopping_list_items FOR SELECT 
USING (
  EXISTS (
    SELECT 1 FROM shopping_lists sl, household_memberships hm 
    WHERE sl.id = shopping_list_items.shopping_list_id 
    AND hm.household_id = sl.household_id 
    AND hm.user_id = auth.uid()
  )
);

CREATE POLICY "Users can manage shopping list items" ON shopping_list_items FOR ALL 
USING (
  EXISTS (
    SELECT 1 FROM shopping_lists sl, household_memberships hm 
    WHERE sl.id = shopping_list_items.shopping_list_id 
    AND hm.household_id = sl.household_id 
    AND hm.user_id = auth.uid()
  )
);

-- Recipe usage: users can only see their own usage
CREATE POLICY "Users can view own recipe usage" ON recipe_usage FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can create own recipe usage" ON recipe_usage FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Ingredients: readable by all authenticated users
CREATE POLICY "Authenticated users can view ingredients" ON ingredients FOR SELECT 
TO authenticated USING (true);

CREATE POLICY "Authenticated users can create ingredients" ON ingredients FOR INSERT 
TO authenticated WITH CHECK (true);