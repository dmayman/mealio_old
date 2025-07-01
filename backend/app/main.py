from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from recipe_scrapers import scrape_html, SCRAPERS
import logging
from typing import List, Optional, Dict, Any
import requests

app = FastAPI(title="Recipe Scraper API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecipeURL(BaseModel):
    url: str

@app.get("/")
async def read_root():
    return {"message": "Recipe Scraper API is running"}

@app.post("/scrape")
async def scrape_recipe(recipe_url: RecipeURL):
    url = recipe_url.url
    logger.info(f"Scraping recipe from URL: {url}")
    
    try:
        # Fetch the HTML content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Create scraper from HTML
        scraper = scrape_html(html=response.text, org_url=url)
        
        # Helper function to safely get attributes
        def safe_get(attr: str, default: Any = None) -> Any:
            try:
                value = getattr(scraper, attr)
                if callable(value):
                    value = value()
                return value or default
            except Exception as e:
                logger.warning(f"Error getting {attr}: {str(e)}")
                return default
        
        # Get recipe data
        name = safe_get('title', 'Untitled Recipe')
        
        # Get ingredients
        ingredients = safe_get('ingredients', [])
        if isinstance(ingredients, str):
            ingredients = [i.strip() for i in ingredients.split('\n') if i.strip()]
        
        # Get instructions
        instructions = safe_get('instructions', '')
        if isinstance(instructions, str):
            instructions = [i.strip() for i in instructions.split('\n') if i.strip()]
        
        # Get image (handle case where it might be a list)
        image = safe_get('image')
        if isinstance(image, list):
            image = image[0] if image else None
        
        # Get source URL
        source_url = safe_get('canonical_url', url) or url
        
        # Construct the recipe data
        recipe_data = {
            "name": name,
            "ingredients": ingredients,
            "instructions": instructions,
            "prepTime": safe_get('prep_time'),
            "cookTime": safe_get('cook_time'),
            "totalTime": safe_get('total_time'),
            "yields": safe_get('yields'),
            "image": image,
            "sourceUrl": source_url,
            "host": safe_get('host', '')
        }
        
        # Validate that we have at least some recipe data
        if not recipe_data["ingredients"] and not recipe_data["instructions"]:
            # Try to get the raw data as a fallback
            try:
                raw_data = safe_get('to_json', {})
                if isinstance(raw_data, dict):
                    if 'ingredients' in raw_data and not recipe_data["ingredients"]:
                        recipe_data["ingredients"] = raw_data['ingredients']
                    if 'instructions' in raw_data and not recipe_data["instructions"]:
                        instructions = raw_data['instructions']
                        if isinstance(instructions, str):
                            instructions = [i.strip() for i in instructions.split('\n') if i.strip()]
                        recipe_data["instructions"] = instructions
            except Exception as e:
                logger.warning(f"Error getting raw data: {str(e)}")
            
            # If we still don't have data, raise an error
            if not recipe_data["ingredients"] and not recipe_data["instructions"]:
                raise ValueError("No recipe data could be extracted from the page")
            
        return recipe_data
        
    except Exception as e:
        logger.error(f"Error scraping recipe: {str(e)}")
        error_detail = str(e)
        
        # Provide more user-friendly error messages for common issues
        if "No schema.org recipe data found" in error_detail:
            error_detail = "This page doesn't contain a recognized recipe format. Please try a different URL."
        elif "No parser for URL" in error_detail:
            error_detail = "This website is not currently supported. Please try a different recipe site."
        elif "Failed to fetch" in error_detail:
            error_detail = "Could not fetch the recipe. Please check the URL and try again."
        elif "404" in error_detail:
            error_detail = "Recipe not found (404 error). Please check the URL and try again."
        elif "403" in error_detail or "Forbidden" in error_detail:
            error_detail = "Access to this recipe is forbidden. The website may be blocking our requests."
            
        raise HTTPException(
            status_code=400,
            detail=error_detail
        )

@app.get("/supported-sites")
async def get_supported_sites():
    """Return a list of supported recipe websites"""
    return {"supported_sites": list(SCRAPERS.keys())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
