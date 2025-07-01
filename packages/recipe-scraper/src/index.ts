import axios from 'axios';
import * as cheerio from 'cheerio';

interface Recipe {
  name: string;
  ingredients: string[];
  instructions: string[];
  prepTime?: string;
  cookTime?: string;
  servings?: string;
}

async function scrapeAllRecipes(url: string): Promise<Recipe> {
  try {
    // Set a user agent to avoid being blocked
    const { data } = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });

    const $ = cheerio.load(data);
    
    // Extract recipe name
    const name = $('h1').first().text().trim();
    
    // Extract ingredients
    const ingredients: string[] = [];
    $('li[data-ingredient-quantity], li[data-testid*="ingredient"]').each((_, el) => {
      const text = $(el).text().replace(/\s+/g, ' ').trim();
      if (text && !text.includes('Add all ingredients to list')) {
        ingredients.push(text);
      }
    });
    
    // If first approach didn't work, try alternative selectors
    if (ingredients.length === 0) {
      $('li[class*="ingredients-item"], div[class*="ingredients-item"]').each((_, el) => {
        const text = $(el).text().replace(/\s+/g, ' ').trim();
        if (text && !text.includes('Add all ingredients to list')) {
          ingredients.push(text);
        }
      });
    }
    
    // Extract instructions
    const instructions: string[] = [];
    $('div[class*="instructions"], ol[class*="instructions"] li, div[data-testid*="instruction"]').each((i, el) => {
      const step = $(el).text().replace(/\s+/g, ' ').trim();
      if (step && step.length > 10) { // Filter out short text that's probably not a step
        instructions.push(`${i + 1}. ${step}`);
      }
    });
    
    // Extract additional metadata
    const metaSelectors = {
      prepTime: ['div[class*="prep"], span[class*="prep"], div[data-testid*="prep"], span[data-testid*="prep"]'],
      cookTime: ['div[class*="cook"], span[class*="cook"], div[data-testid*="cook"], span[data-testid*="cook"]'],
      servings: ['div[class*="servings"], span[class*="servings"], div[data-testid*="servings"], span[data-testid*="servings"]']
    };
    
    const meta: Record<string, string> = {};
    
    Object.entries(metaSelectors).forEach(([key, selectors]) => {
      for (const selector of selectors) {
        const element = $(selector).first();
        if (element.length) {
          const text = element.text().trim();
          if (text) {
            meta[key] = text;
            break;
          }
        }
      }
    });

    return {
      name,
      ingredients,
      instructions,
      ...(meta.prepTime && { prepTime: meta.prepTime }),
      ...(meta.cookTime && { cookTime: meta.cookTime }),
      ...(meta.servings && { servings: meta.servings })
    };
  } catch (error) {
    console.error('Error scraping recipe:', error);
    throw error;
  }
}

async function main() {
  const url = process.argv[2];
  if (!url) {
    console.error('Usage: pnpm --filter @mealio/recipe-scraper dev <recipe-url>');
    process.exit(1);
  }

  try {
    const recipe = await scrapeAllRecipes(url);
    console.log(JSON.stringify(recipe, null, 2));
  } catch (error) {
    console.error('Failed to scrape recipe:', error);
    process.exit(1);
  }
}

main();