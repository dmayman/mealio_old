-- Create a test user in local Supabase
-- This user will be used for testing the recipe flow

-- Insert test user directly into auth.users table
INSERT INTO auth.users (
    id,
    instance_id,
    email,
    encrypted_password,
    email_confirmed_at,
    created_at,
    updated_at,
    raw_user_meta_data,
    aud,
    role
) VALUES (
    '11111111-1111-1111-1111-111111111111'::uuid,
    '00000000-0000-0000-0000-000000000000'::uuid,
    'test@mealio.com',
    crypt('testpassword123', gen_salt('bf')),
    now(),
    now(),
    now(),
    '{"display_name": "Test User"}'::jsonb,
    'authenticated',
    'authenticated'
)
ON CONFLICT (id) DO NOTHING;

-- The user_profiles record should be created automatically by the trigger
-- But let's verify/create it manually if needed
INSERT INTO user_profiles (id, display_name)
VALUES (
    '11111111-1111-1111-1111-111111111111'::uuid,
    'Test User'
)
ON CONFLICT (id) DO UPDATE SET
    display_name = EXCLUDED.display_name;

-- Create a test household for the user
INSERT INTO households (id, name, created_by, invite_code)
VALUES (
    '22222222-2222-2222-2222-222222222222'::uuid,
    'Test Household',
    '11111111-1111-1111-1111-111111111111'::uuid,
    'TEST123'
)
ON CONFLICT (id) DO NOTHING;

-- Add user to the household
INSERT INTO household_memberships (household_id, user_id, role)
VALUES (
    '22222222-2222-2222-2222-222222222222'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    'admin'
)
ON CONFLICT (user_id) DO NOTHING;

-- Update user profile with current household
UPDATE user_profiles 
SET current_household_id = '22222222-2222-2222-2222-222222222222'::uuid
WHERE id = '11111111-1111-1111-1111-111111111111'::uuid;

-- Verify the setup
SELECT 
    u.email,
    p.display_name,
    h.name as household_name,
    hm.role
FROM auth.users u
JOIN user_profiles p ON p.id = u.id
LEFT JOIN household_memberships hm ON hm.user_id = u.id
LEFT JOIN households h ON h.id = hm.household_id
WHERE u.email = 'test@mealio.com';