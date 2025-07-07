-- Mealio Seed Data for Testing
-- This creates sample data to test the household functionality
-- NOTE: This creates test auth users first, then user profiles

-- Create test auth users (normally done through signup)
-- In production, users would sign up through your app
INSERT INTO auth.users (
  id,
  instance_id,
  email,
  encrypted_password,
  email_confirmed_at,
  created_at,
  updated_at,
  raw_app_meta_data,
  raw_user_meta_data,
  is_super_admin,
  role
) VALUES 
  (
    '550e8400-e29b-41d4-a716-446655440001',
    '00000000-0000-0000-0000-000000000000',
    'alice@example.com',
    '$2a$10$placeholder.hash.for.testing.only.not.real.password',
    NOW(),
    NOW(),
    NOW(),
    '{"provider": "email", "providers": ["email"]}',
    '{"display_name": "Alice Johnson"}',
    false,
    'authenticated'
  ),
  (
    '550e8400-e29b-41d4-a716-446655440002',
    '00000000-0000-0000-0000-000000000000',
    'bob@example.com',
    '$2a$10$placeholder.hash.for.testing.only.not.real.password',
    NOW(),
    NOW(),
    NOW(),
    '{"provider": "email", "providers": ["email"]}',
    '{"display_name": "Bob Smith"}',
    false,
    'authenticated'
  ),
  (
    '550e8400-e29b-41d4-a716-446655440003',
    '00000000-0000-0000-0000-000000000000',
    'charlie@example.com',
    '$2a$10$placeholder.hash.for.testing.only.not.real.password',
    NOW(),
    NOW(),
    NOW(),
    '{"provider": "email", "providers": ["email"]}',
    '{"display_name": "Charlie Brown"}',
    false,
    'authenticated'
  ),
  (
    '550e8400-e29b-41d4-a716-446655440004',
    '00000000-0000-0000-0000-000000000000',
    'diana@example.com',
    '$2a$10$placeholder.hash.for.testing.only.not.real.password',
    NOW(),
    NOW(),
    NOW(),
    '{"provider": "email", "providers": ["email"]}',
    '{"display_name": "Diana Wilson"}',
    false,
    'authenticated'
  )
ON CONFLICT (id) DO NOTHING;

-- The user profiles will be created automatically by the trigger
-- But let's make sure they exist with the right display names
INSERT INTO user_profiles (id, display_name) VALUES 
  ('550e8400-e29b-41d4-a716-446655440001', 'Alice Johnson'),
  ('550e8400-e29b-41d4-a716-446655440002', 'Bob Smith'),
  ('550e8400-e29b-41d4-a716-446655440003', 'Charlie Brown'),
  ('550e8400-e29b-41d4-a716-446655440004', 'Diana Wilson')
ON CONFLICT (id) DO UPDATE SET display_name = EXCLUDED.display_name;

-- Insert sample household
INSERT INTO households (id, name, created_by, invite_code) VALUES 
  ('660e8400-e29b-41d4-a716-446655440001', 'The Johnson-Smith Family', '550e8400-e29b-41d4-a716-446655440001', 'FAMILY01');

-- Insert household memberships
INSERT INTO household_memberships (household_id, user_id, role) VALUES 
  ('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'admin'),
  ('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440002', 'member');

-- Update user profiles with current household
UPDATE user_profiles SET current_household_id = '660e8400-e29b-41d4-a716-446655440001' 
WHERE id IN ('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440002');

-- Insert sample ingredients
INSERT INTO ingredients (id, name, category) VALUES 
  ('770e8400-e29b-41d4-a716-446655440001', 'Chicken Breast', 'Protein'),
  ('770e8400-e29b-41d4-a716-446655440002', 'Broccoli', 'Vegetables'),
  ('770e8400-e29b-41d4-a716-446655440003', 'Rice', 'Grains'),
  ('770e8400-e29b-41d4-a716-446655440004', 'Olive Oil', 'Oils'),
  ('770e8400-e29b-41d4-a716-446655440005', 'Garlic', 'Vegetables'),
  ('770e8400-e29b-41d4-a716-446655440006', 'Salt', 'Seasonings'),
  ('770e8400-e29b-41d4-a716-446655440007', 'Black Pepper', 'Seasonings'),
  ('770e8400-e29b-41d4-a716-446655440008', 'Soy Sauce', 'Condiments'),
  ('770e8400-e29b-41d4-a716-446655440009', 'Eggs', 'Protein'),
  ('770e8400-e29b-41d4-a716-446655440010', 'Onion', 'Vegetables');

-- Insert sample recipes
INSERT INTO recipes (id, user_id, title, description, instructions, prep_time, cook_time, servings, difficulty_level, shared_with_household) VALUES 
  ('880e8400-e29b-41d4-a716-446655440001', 
   '550e8400-e29b-41d4-a716-446655440001', 
   'Chicken and Broccoli Stir Fry', 
   'A quick and healthy stir fry perfect for weeknight dinners',
   ARRAY['Cut chicken into bite-sized pieces', 'Heat oil in large pan', 'Cook chicken until golden', 'Add broccoli and garlic', 'Stir in soy sauce', 'Serve over rice'],
   15, 20, 4, 'beginner', true),
  ('880e8400-e29b-41d4-a716-446655440002', 
   '550e8400-e29b-41d4-a716-446655440002', 
   'Simple Fried Rice', 
   'Easy fried rice using leftover rice',
   ARRAY['Heat oil in pan', 'Scramble eggs and set aside', 'Sauté onion and garlic', 'Add rice and break up clumps', 'Mix in eggs and soy sauce', 'Season with salt and pepper'],
   10, 15, 3, 'beginner', true),
  ('880e8400-e29b-41d4-a716-446655440003', 
   '550e8400-e29b-41d4-a716-446655440003', 
   'Charlies Secret Pasta', 
   'A family secret recipe passed down for generations',
   ARRAY['Boil water for pasta', 'Prepare secret sauce (family recipe)', 'Cook pasta al dente', 'Combine with sauce', 'Serve immediately'],
   5, 25, 6, 'intermediate', false); -- Charlie's recipe is not shared

-- Insert recipe ingredients
INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, order_index) VALUES 
  -- Chicken and Broccoli Stir Fry
  ('880e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440001', 1.00, 'lb', 1),
  ('880e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440002', 2.00, 'cups', 2),
  ('880e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440003', 2.00, 'cups', 3),
  ('880e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440004', 2.00, 'tbsp', 4),
  ('880e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440005', 3.00, 'cloves', 5),
  ('880e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440008', 3.00, 'tbsp', 6),
  -- Simple Fried Rice
  ('880e8400-e29b-41d4-a716-446655440002', '770e8400-e29b-41d4-a716-446655440003', 3.00, 'cups', 1),
  ('880e8400-e29b-41d4-a716-446655440002', '770e8400-e29b-41d4-a716-446655440009', 3.00, 'large', 2),
  ('880e8400-e29b-41d4-a716-446655440002', '770e8400-e29b-41d4-a716-446655440010', 1.00, 'medium', 3),
  ('880e8400-e29b-41d4-a716-446655440002', '770e8400-e29b-41d4-a716-446655440005', 2.00, 'cloves', 4),
  ('880e8400-e29b-41d4-a716-446655440002', '770e8400-e29b-41d4-a716-446655440004', 2.00, 'tbsp', 5),
  ('880e8400-e29b-41d4-a716-446655440002', '770e8400-e29b-41d4-a716-446655440008', 2.00, 'tbsp', 6);

-- Insert sample meal plan
INSERT INTO meal_plans (id, user_id, household_id, week_start, name) VALUES 
  ('990e8400-e29b-41d4-a716-446655440001', 
   '550e8400-e29b-41d4-a716-446655440001', 
   '660e8400-e29b-41d4-a716-446655440001', 
   '2024-07-08', 
   'Week of July 8th');

-- Insert planned meals
INSERT INTO planned_meals (meal_plan_id, recipe_id, planned_date, meal_type) VALUES 
  ('990e8400-e29b-41d4-a716-446655440001', '880e8400-e29b-41d4-a716-446655440001', '2024-07-08', 'dinner'),
  ('990e8400-e29b-41d4-a716-446655440001', '880e8400-e29b-41d4-a716-446655440002', '2024-07-09', 'lunch'),
  ('990e8400-e29b-41d4-a716-446655440001', '880e8400-e29b-41d4-a716-446655440001', '2024-07-10', 'dinner');

-- Insert sample shopping list
INSERT INTO shopping_lists (id, meal_plan_id, user_id, household_id, name) VALUES 
  ('aa0e8400-e29b-41d4-a716-446655440001', 
   '990e8400-e29b-41d4-a716-446655440001', 
   '550e8400-e29b-41d4-a716-446655440001', 
   '660e8400-e29b-41d4-a716-446655440001', 
   'Grocery List - Week of July 8th');

-- Insert shopping list items
INSERT INTO shopping_list_items (shopping_list_id, ingredient_id, quantity, unit, category, order_index) VALUES 
  ('aa0e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440001', 2.00, 'lb', 'Meat', 1),
  ('aa0e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440002', 4.00, 'cups', 'Produce', 2),
  ('aa0e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440003', 5.00, 'cups', 'Pantry', 3),
  ('aa0e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440009', 6.00, 'large', 'Dairy', 4),
  ('aa0e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440010', 2.00, 'medium', 'Produce', 5);

-- Insert some recipe usage tracking
INSERT INTO recipe_usage (user_id, recipe_id, rating, notes, cooking_time_actual) VALUES 
  ('550e8400-e29b-41d4-a716-446655440001', '880e8400-e29b-41d4-a716-446655440001', 5, 'Perfect for busy weeknights!', 25),
  ('550e8400-e29b-41d4-a716-446655440002', '880e8400-e29b-41d4-a716-446655440002', 4, 'Kids loved it, will make again', 18),
  ('550e8400-e29b-41d4-a716-446655440001', '880e8400-e29b-41d4-a716-446655440002', 4, 'Great way to use leftover rice', 20);