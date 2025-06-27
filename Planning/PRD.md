# Weekly Meal Planning App – PRD

## Overview
A meal planning tool for individuals and families to easily manage their weekly food needs—from deciding what to eat, to buying groceries, to cooking meals. The app reduces the cognitive load of grocery shopping and meal planning, helping people feel more in control of what they eat without being overwhelmed.

This is a mobile-first product, but should be web accessible too.

## Problem Statement
Buying food and cooking regularly is a burden. Many people want to be healthy and plan meals but fall behind due to lack of tools to organize recipes, plan meals around their schedule, and shop efficiently. This leads to decision fatigue, wasted groceries, and last-minute takeout.

## Users
- Adults or families who cook at home 3+ times a week and want to eat healthier or reduce friction around food.

## Key Features

### 1. Recipe Supply
- **Recipe Ingestion (P0)**: Users can paste recipe URLs; app scrapes any website using metadata or parsing techniques to extract ingredients and instructions. Also supports manual entry.
- **Recipe Recommendations (P2)**: Suggests recipes based on user preferences and pantry gaps.
- **Recipe Usage History (P0)**: Tracks how often you use recipes and which you’ve liked for smarter future planning.

### 2. Meal Planning
- **Queue Recipes (P0)**: Add recipes from your saved list to a planning queue.
- **Auto-Generate Grocery List (P0)**: Aggregates all ingredients from planned meals into a master shopping list.
- **Weekly Planning Nudges (P0)**: App prompts you weekly to plan meals.
- **Calendar Availability Insight (P1)**: Reads your calendar to estimate how many meals you might want to plan for, without assigning them to specific days or times.
- **Recipe Suggestions (P1)**: Suggest meals based on your bank. Possibly “Tinder”-style swipe interface for accepting/rejecting suggestions.

### 3. Shopping
- **Smart Shopping List (P1)**: Generates a categorized list with checkboxes for in-store use.
- **Instacart Export (P2)**: Bulk export shopping list into Instacart or other grocery apps.
- **Select All/None (P1)**: Easy toggling for editing and copying list content.

### 4. Cooking
- **Cooking Queue (P0)**: Shows only the meals you’ve planned for the week.
- **Cooking Mode (P0)**: Displays recipe instructions alongside ingredient amounts in-line for ease of use.
- **Clear After Cooking (P0)**: Marks recipe as done and removes from queue.

## Prioritization
**P0 – Core MVP**
- Recipe ingestion (scraper/manual)
- Recipe usage tracking
- Meal planning flow (w/ calendar availability insight)
- Grocery list aggregation
- Cooking mode with in-line quantities

**P1 – Automations/Integrations**
- Calendar integration (read-only)
- Recipe suggestions
- Smart shopping list organization
- Instacart export

**P2 – Generative Enhancements**
- Recipe generation
- Preference-based recommendations

## Open Questions
- Should users be able to track pantry items or inventory?
- Will recipes have tagging or dietary filters?
- What platforms are we targeting first—web, iOS, both?
- What third-party APIs exist for categorizing or organizing food items by type or grocery aisle?

---

Next Steps:
- Define onboarding experience
- Identify third-party APIs (e.g., recipe parsers, grocery categorization, calendar access)
- Start with a simple weekly planning loop