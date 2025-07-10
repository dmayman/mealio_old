-- Migration: Implement Recipe Household Access Model
-- This migration implements the new recipe ownership model where:
-- 1. Recipe access is tracked per household over time
-- 2. Households retain access to recipes even after creators leave
-- 3. Users joining households inherit access to household recipe collection

-- Create recipe_household_access table to track persistent access grants
CREATE TABLE recipe_household_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    household_id UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique access grants per recipe-household pair
    UNIQUE(recipe_id, household_id)
);

-- Add indexes for performance
CREATE INDEX idx_recipe_household_access_recipe_id ON recipe_household_access(recipe_id);
CREATE INDEX idx_recipe_household_access_household_id ON recipe_household_access(household_id);
CREATE INDEX idx_recipe_household_access_granted_at ON recipe_household_access(granted_at);

-- Enable RLS on the new table
ALTER TABLE recipe_household_access ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can view access grants for households they belong to
CREATE POLICY "Users can view household recipe access" ON recipe_household_access FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM household_memberships hm
        WHERE hm.household_id = recipe_household_access.household_id
        AND hm.user_id = auth.uid()
    )
);

-- RLS Policy: Users can create access grants for their own recipes to their household
CREATE POLICY "Users can grant access to their recipes" ON recipe_household_access FOR INSERT
WITH CHECK (
    -- User owns the recipe
    EXISTS (
        SELECT 1 FROM recipes r
        WHERE r.id = recipe_household_access.recipe_id
        AND r.user_id = auth.uid()
    )
    AND
    -- User is member of the target household
    EXISTS (
        SELECT 1 FROM household_memberships hm
        WHERE hm.household_id = recipe_household_access.household_id
        AND hm.user_id = auth.uid()
    )
);

-- RLS Policy: Users can revoke access grants for their own recipes
CREATE POLICY "Users can revoke access to their recipes" ON recipe_household_access FOR DELETE
USING (
    EXISTS (
        SELECT 1 FROM recipes r
        WHERE r.id = recipe_household_access.recipe_id
        AND r.user_id = auth.uid()
    )
);

-- Update existing RLS policies on recipes table to use new access model
DROP POLICY IF EXISTS "Users can view accessible recipes" ON recipes;

-- New comprehensive recipe access policy
CREATE POLICY "Users can view accessible recipes" ON recipes FOR SELECT
USING (
    -- User owns the recipe
    user_id = auth.uid()
    OR
    -- Recipe is shared with user's current household
    EXISTS (
        SELECT 1 FROM recipe_household_access rha
        JOIN household_memberships hm ON hm.household_id = rha.household_id
        WHERE rha.recipe_id = recipes.id
        AND hm.user_id = auth.uid()
    )
);

-- Users can only update/delete their own recipes (unchanged)
CREATE POLICY "Users can modify their own recipes" ON recipes FOR UPDATE
USING (user_id = auth.uid());

CREATE POLICY "Users can delete their own recipes" ON recipes FOR DELETE
USING (user_id = auth.uid());

-- Data Migration: Convert existing shared recipes to explicit household access grants
-- This preserves current sharing behavior while transitioning to the new model
INSERT INTO recipe_household_access (recipe_id, household_id, granted_by, granted_at)
SELECT DISTINCT 
    r.id as recipe_id,
    hm.household_id,
    r.user_id as granted_by,
    r.created_at as granted_at
FROM recipes r
JOIN household_memberships hm ON hm.user_id = r.user_id
WHERE r.shared_with_household = true
ON CONFLICT (recipe_id, household_id) DO NOTHING;

-- Function to automatically grant household access when a recipe is shared
CREATE OR REPLACE FUNCTION auto_grant_household_access()
RETURNS TRIGGER AS $$
BEGIN
    -- If recipe is being shared with household, grant access to user's current household
    IF NEW.shared_with_household = true AND (OLD.shared_with_household IS NULL OR OLD.shared_with_household = false) THEN
        INSERT INTO recipe_household_access (recipe_id, household_id, granted_by)
        SELECT NEW.id, hm.household_id, NEW.user_id
        FROM household_memberships hm
        WHERE hm.user_id = NEW.user_id
        ON CONFLICT (recipe_id, household_id) DO NOTHING;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically grant access when shared_with_household is set to true
CREATE TRIGGER trigger_auto_grant_household_access
    AFTER UPDATE OF shared_with_household ON recipes
    FOR EACH ROW
    EXECUTE FUNCTION auto_grant_household_access();

-- Function to grant access to new household members for existing shared recipes
CREATE OR REPLACE FUNCTION grant_access_to_new_member()
RETURNS TRIGGER AS $$
BEGIN
    -- When a user joins a household, they get access to all recipes already shared with that household
    -- This is automatic through the RLS policy, but we might want to track this event
    
    -- For now, just return the new record as this is handled by the access table
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for when users join households (access is automatic via the access table)
CREATE TRIGGER trigger_grant_access_to_new_member
    AFTER INSERT ON household_memberships
    FOR EACH ROW
    EXECUTE FUNCTION grant_access_to_new_member();

-- Add helpful comments
COMMENT ON TABLE recipe_household_access IS 'Tracks which households have been granted access to recipes over time';
COMMENT ON COLUMN recipe_household_access.recipe_id IS 'The recipe being shared';
COMMENT ON COLUMN recipe_household_access.household_id IS 'The household that has access';
COMMENT ON COLUMN recipe_household_access.granted_at IS 'When access was first granted';
COMMENT ON COLUMN recipe_household_access.granted_by IS 'User who granted the access (recipe owner)';