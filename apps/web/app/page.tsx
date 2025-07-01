'use client';

import { useState } from 'react';

export default function Home() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [recipe, setRecipe] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url) {
      setError('Please enter a recipe URL');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      
      const response = await fetch('/api/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch recipe');
      }

      const data = await response.json();
      setRecipe(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-gray-900 mb-2">Mealio Recipe Scraper</h1>
          <p className="text-gray-600">Paste a recipe URL to get started</p>
        </div>

        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
                Recipe URL
              </label>
              <div className="mt-1">
                <input
                  type="url"
                  id="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://www.allrecipes.com/recipe/..."
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-50 text-red-700 text-sm rounded-md">
                <p>{error}</p>
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
              >
                {isLoading ? 'Scraping...' : 'Get Recipe'}
              </button>
            </div>
          </form>
        </div>

        {recipe && (
          <div className="bg-white shadow overflow-hidden rounded-lg">
            <div className="px-4 py-5 sm:px-6">
              <h2 className="text-lg font-medium text-gray-900">{recipe.name}</h2>
              <p className="mt-1 text-sm text-gray-500">
                Source: <a href={recipe.sourceUrl} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{recipe.sourceUrl}</a>
              </p>
            </div>
            
            <div className="border-t border-gray-200">
              <dl>
                <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Ingredients</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                    <ul className="list-disc pl-5 space-y-1">
                      {recipe.ingredients.map((ingredient: string, i: number) => (
                        <li key={i}>{ingredient}</li>
                      ))}
                    </ul>
                  </dd>
                </div>
                
                <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Instructions</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                    <ol className="list-decimal pl-5 space-y-2">
                      {recipe.instructions.map((instruction: string, i: number) => (
                        <li key={i} className="mb-2">{instruction}</li>
                      ))}
                    </ol>
                  </dd>
                </div>
                
                {(recipe.prepTime || recipe.cookTime || recipe.servings) && (
                  <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">Details</dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                      <div className="grid grid-cols-3 gap-4">
                        {recipe.prepTime && (
                          <div>
                            <p className="text-xs text-gray-500">Prep Time</p>
                            <p>{recipe.prepTime}</p>
                          </div>
                        )}
                        {recipe.cookTime && (
                          <div>
                            <p className="text-xs text-gray-500">Cook Time</p>
                            <p>{recipe.cookTime}</p>
                          </div>
                        )}
                        {recipe.servings && (
                          <div>
                            <p className="text-xs text-gray-500">Servings</p>
                            <p>{recipe.servings}</p>
                          </div>
                        )}
                      </div>
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
