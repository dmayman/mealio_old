#!/usr/bin/env python3
"""
Recipe Scraper CLI Test Tool
This script helps you test recipe-scrapers and see the data structure it returns.
"""

import json
from recipe_scrapers import scrape_html, SCRAPERS
import requests
from pprint import pprint


def get_all_attributes(scraper):
    """Extract all available attributes from the scraper object."""
    recipe_data = {}
    
    # List of common recipe-scrapers attributes
    attributes = [
        'title', 'total_time', 'prep_time', 'cook_time', 'yields', 'servings',
        'ingredients', 'instructions', 'image', 'host', 'canonical_url',
        'description', 'cuisine', 'category', 'keywords', 'nutrients',
        'author', 'difficulty', 'equipment', 'language', 'site_name'
    ]
    
    for attr in attributes:
        try:
            if hasattr(scraper, attr):
                value = getattr(scraper, attr)
                if callable(value):
                    value = value()
                recipe_data[attr] = value
        except Exception as e:
            recipe_data[attr] = f"Error: {str(e)}"
    
    return recipe_data


def scrape_recipe(url):
    """Scrape a recipe from the given URL."""
    print(f"🔍 Scraping recipe from: {url}")
    print("-" * 60)
    
    try:
        # Fetch the HTML
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Create scraper
        scraper = scrape_html(html=response.text, org_url=url)
        
        # Get all available data
        recipe_data = get_all_attributes(scraper)
        
        # Display results
        print("✅ Recipe scraped successfully!")
        print(f"🌐 Host: {scraper.host()}")
        print(f"📝 Title: {recipe_data.get('title', 'N/A')}")
        print("\n" + "=" * 60)
        print("COMPLETE RECIPE DATA STRUCTURE:")
        print("=" * 60)
        
        # Pretty print the complete data
        pprint(recipe_data, width=80, depth=3)
        
        # Show raw JSON structure
        print("\n" + "=" * 60)
        print("JSON FORMAT:")
        print("=" * 60)
        print(json.dumps(recipe_data, indent=2, default=str))
        
        return recipe_data
        
    except Exception as e:
        print(f"❌ Error scraping recipe: {str(e)}")
        return None


def show_supported_sites():
    """Display supported recipe websites."""
    print("🌐 Supported Recipe Websites:")
    print("-" * 40)
    sites = list(SCRAPERS.keys())
    for i, site in enumerate(sorted(sites), 1):
        print(f"{i:3d}. {site}")
    print(f"\nTotal: {len(sites)} supported sites")


def main():
    """Main CLI interface."""
    print("🍳 Recipe Scraper Test Tool")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Scrape a recipe URL")
        print("2. Show supported websites")
        print("3. Test with sample URLs")
        print("4. Exit")
        
        choice = input("\nChoose an option (1-4): ").strip()
        
        if choice == "1":
            url = input("\n📝 Enter recipe URL: ").strip()
            if url:
                result = scrape_recipe(url)
                if result:
                    save = input("\n💾 Save to file? (y/N): ").strip().lower()
                    if save == 'y':
                        filename = f"scraped_recipe_{url.split('/')[-1][:20]}.json"
                        with open(filename, 'w') as f:
                            json.dump(result, f, indent=2, default=str)
                        print(f"✅ Saved to {filename}")
            else:
                print("❌ Please enter a valid URL")
                
        elif choice == "2":
            show_supported_sites()
            
        elif choice == "3":
            print("\n🧪 Testing with sample URLs:")
            sample_urls = [
                "https://www.allrecipes.com/recipe/213742/cheesy-chicken-broccoli-casserole/",
                "https://www.foodnetwork.com/recipes/alton-brown/baked-macaroni-and-cheese-recipe-1939524",
                "https://www.seriouseats.com/the-best-slow-cooked-italian-american-tomato-sauce-recipe"
            ]
            
            for i, url in enumerate(sample_urls, 1):
                print(f"\n{i}. Testing: {url}")
                proceed = input("   Scrape this URL? (y/N): ").strip().lower()
                if proceed == 'y':
                    scrape_recipe(url)
                    input("\n   Press Enter to continue...")
                    
        elif choice == "4":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()