import { NextResponse } from 'next/server';

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:8001';

export async function POST(request: Request) {
  try {
    const { url } = await request.json();
    
    if (!url) {
      return NextResponse.json(
        { error: 'URL is required' },
        { status: 400 }
      );
    }

    // Forward the request to the Python backend
    const response = await fetch(`${PYTHON_BACKEND_URL}/scrape`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to scrape recipe');
    }

    const recipeData = await response.json();
    
    // Transform the data to match our frontend expectations
    return NextResponse.json({
      name: recipeData.name,
      ingredients: recipeData.ingredients || [],
      instructions: Array.isArray(recipeData.instructions) 
        ? recipeData.instructions 
        : (recipeData.instructions || '').split('\n').filter(Boolean),
      prepTime: recipeData.prepTime,
      cookTime: recipeData.cookTime,
      servings: recipeData.yields,
      sourceUrl: recipeData.sourceUrl || url,
      image: recipeData.image
    });
    
  } catch (error) {
    console.error('Error scraping recipe:', error);
    return NextResponse.json(
      { 
        error: 'Failed to scrape recipe',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
