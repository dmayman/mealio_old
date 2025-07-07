# Supabase Setup Guide for Mealio

## Overview
This guide will help you set up the Mealio database schema in Supabase with proper authentication integration.

## Key Changes Made for Supabase Auth

### Database Schema
- **`user_profiles` table**: Extends Supabase's `auth.users` with app-specific data
- **All foreign keys**: Now reference `auth.users(id)` instead of a custom users table
- **Row Level Security (RLS)**: Comprehensive policies for data security
- **Auto-trigger**: Creates user profile when auth user signs up

### Authentication Flow
1. Users sign up/login through Supabase Auth
2. `handle_new_user()` trigger automatically creates user profile
3. All API requests use `auth.uid()` for user identification
4. RLS policies enforce data access rules

## Setup Steps

### 1. Link to Your Supabase Project
```bash
# Link to your existing Supabase project
supabase link --project-ref YOUR_PROJECT_REF

# Or create a new project
supabase projects create mealio
```

### 2. Apply the Schema
```bash
# Apply the schema directly from the database/schema.sql file
psql -h db.your-project.supabase.co -U postgres -d postgres < database/schema.sql

# Or if using local development:
supabase start
psql -h localhost -p 54322 -U postgres -d postgres < database/schema.sql
```

### 3. Enable Authentication
In your Supabase dashboard:
1. Go to Authentication → Settings
2. Enable email/password authentication
3. Configure any social providers you want
4. Set up email templates if needed

### 4. Create Test Users (Optional)
For testing, create users in Supabase Auth:
1. Go to Authentication → Users
2. Add users manually, or
3. Use the signup API from your app

### 5. Apply Seed Data (Optional)
```bash
# Connect to your database and run
psql -h db.your-project.supabase.co -U postgres -d postgres < supabase/seed.sql

# Or if using local development:
psql -h localhost -p 54322 -U postgres -d postgres < supabase/seed.sql
```

**Note**: The seed data contains test user profiles. In production, user profiles are created automatically when users sign up through Supabase Auth.

## Key Features Implemented

### 🔐 Row Level Security (RLS)
- **User Profiles**: Users can only see/edit their own
- **Households**: Members can see household data
- **Recipes**: Personal + shared household recipes
- **Meal Plans**: Household-scoped collaboration
- **Shopping Lists**: Household-scoped with member access

### 🏠 Household System
- **Invite Codes**: Easy household joining
- **Role Management**: Admin vs Member permissions
- **Single Household**: Users can only be in one household
- **Automatic Profile Creation**: Via database trigger

### 🍳 Recipe Sharing
- **Personal Ownership**: Users own their recipes
- **Household Sharing**: Toggle to share with household
- **Access Control**: RLS ensures proper access

### 📝 Collaborative Planning
- **Household Meal Plans**: All members can collaborate
- **Shared Shopping Lists**: Household-wide grocery planning
- **Usage Tracking**: Personal recipe usage and ratings

## Environment Variables

Update your `.env` file:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Database Configuration (for direct SQL access)
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
```

## API Integration

Your FastAPI backend will need to:
1. **Validate JWT tokens** from Supabase Auth
2. **Extract user ID** from `auth.uid()`
3. **Use RLS policies** for automatic data filtering
4. **Handle user context** in all database operations

## Testing the Setup

1. **Create a test user** in Supabase Auth
2. **Run the seed data** with the user's actual ID
3. **Test API endpoints** with proper auth headers
4. **Verify RLS policies** are working correctly

## Next Steps

You'll need to update your FastAPI backend to:
- Remove manual user management
- Integrate with Supabase Auth JWT validation
- Use `auth.uid()` for user context
- Leverage RLS for automatic data filtering

This setup provides a secure, scalable foundation for the household collaboration features while maintaining proper authentication and authorization.