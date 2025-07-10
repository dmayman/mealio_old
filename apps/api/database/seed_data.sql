-- Seed data for Mealio database
-- Common ingredients and categories for testing

-- Insert common ingredient categories
INSERT INTO ingredients (name, category) VALUES
-- Vegetables
('onion', 'vegetables'),
('garlic', 'vegetables'),
('tomato', 'vegetables'),
('bell pepper', 'vegetables'),
('carrot', 'vegetables'),
('celery', 'vegetables'),
('spinach', 'vegetables'),
('broccoli', 'vegetables'),
('mushrooms', 'vegetables'),
('potato', 'vegetables'),

-- Proteins
('chicken breast', 'proteins'),
('ground beef', 'proteins'),
('salmon', 'proteins'),
('eggs', 'proteins'),
('tofu', 'proteins'),
('black beans', 'proteins'),

-- Dairy
('milk', 'dairy'),
('butter', 'dairy'),
('cheddar cheese', 'dairy'),
('parmesan cheese', 'dairy'),
('cream cheese', 'dairy'),
('greek yogurt', 'dairy'),

-- Pantry staples
('olive oil', 'pantry'),
('salt', 'pantry'),
('black pepper', 'pantry'),
('flour', 'pantry'),
('sugar', 'pantry'),
('rice', 'pantry'),
('pasta', 'pantry'),
('breadcrumbs', 'pantry'),
('baking powder', 'pantry'),
('vanilla extract', 'pantry'),

-- Herbs and spices
('basil', 'herbs_spices'),
('oregano', 'herbs_spices'),
('thyme', 'herbs_spices'),
('rosemary', 'herbs_spices'),
('paprika', 'herbs_spices'),
('cumin', 'herbs_spices'),
('chili powder', 'herbs_spices'),

-- Condiments
('soy sauce', 'condiments'),
('worcestershire sauce', 'condiments'),
('hot sauce', 'condiments'),
('mayonnaise', 'condiments'),
('mustard', 'condiments'),
('ketchup', 'condiments');

-- Sample test user (you'll want to replace with actual Supabase auth integration)
INSERT INTO users (id, email, name) VALUES 
('00000000-0000-0000-0000-000000000001', 'test@example.com', 'Test User');

-- Sample recipe
INSERT INTO recipes (id, user_id, title, description, instructions, prep_time, cook_time, servings, difficulty_level, source_type) VALUES 
('00000000-0000-0000-0000-000000000001', 
 '00000000-0000-0000-0000-000000000001',
 'Simple Pasta with Garlic',
 'A quick and easy pasta dish perfect for weeknight dinners',
 ARRAY[
   'Bring a large pot of salted water to boil',
   'Cook pasta according to package directions',
   'While pasta cooks, heat olive oil in a large skillet',
   'Add minced garlic and cook until fragrant, about 1 minute',
   'Drain pasta and add to skillet with garlic oil',
   'Toss with parmesan cheese and season with salt and pepper',
   'Serve immediately'
 ],
 10, 15, 4, 'beginner', 'manual');

-- Sample recipe ingredients
INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, order_index) VALUES 
('00000000-0000-0000-0000-000000000001', (SELECT id FROM ingredients WHERE name = 'pasta'), 1, 'lb', 1),
('00000000-0000-0000-0000-000000000001', (SELECT id FROM ingredients WHERE name = 'garlic'), 3, 'cloves', 2),
('00000000-0000-0000-0000-000000000001', (SELECT id FROM ingredients WHERE name = 'olive oil'), 3, 'tbsp', 3),
('00000000-0000-0000-0000-000000000001', (SELECT id FROM ingredients WHERE name = 'parmesan cheese'), 0.5, 'cup', 4),
('00000000-0000-0000-0000-000000000001', (SELECT id FROM ingredients WHERE name = 'salt'), 1, 'tsp', 5),
('00000000-0000-0000-0000-000000000001', (SELECT id FROM ingredients WHERE name = 'black pepper'), 0.5, 'tsp', 6);