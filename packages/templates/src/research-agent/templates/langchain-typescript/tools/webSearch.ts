import { Tool } from '@langchain/core/tools';
import { z } from 'zod';

// Input schema for the web search tool
const WebSearchSchema = z.object({
  query: z.string().describe('Search query to find information on the web'),
  numResults: z.number().optional().describe('Number of results to return (default: 5)'),
});

export class WebSearchTool extends Tool {
  name = 'web_search';
  description = 'Search the web for information on any topic. Provides links and snippets from multiple sources.';
  schema = WebSearchSchema;

  constructor() {
    super();
  }

  async _call(input: z.infer<typeof WebSearchSchema>): Promise<string> {
    const { query, numResults = 5 } = input;

    try {
      // Check for available search APIs in order of preference
      if (process.env.BRAVE_API_KEY) {
        return await this.searchWithBrave(query, numResults);
      } else if (process.env.SERPAPI_KEY) {
        return await this.searchWithSerpAPI(query, numResults);
      } else if (process.env.TAVILY_API_KEY) {
        return await this.searchWithTavily(query, numResults);
      } else {
        // Fallback to placeholder search
        return this.mockSearch(query, numResults);
      }
    } catch (error) {
      console.error(`Web search error: ${error}`);
      return this.mockSearch(query, numResults);
    }
  }

  private async searchWithBrave(query: string, numResults: number): Promise<string> {
    const response = await fetch('https://api.search.brave.com/res/v1/web/search', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': process.env.BRAVE_API_KEY!,
      },
      body: new URLSearchParams({
        q: query,
        count: numResults.toString(),
      }),
    });

    if (!response.ok) {
      throw new Error(`Brave Search API error: ${response.status}`);
    }

    const data = await response.json();
    const results = data.web?.results || [];

    if (results.length === 0) {
      return `No results found for "${query}"`;
    }

    const formattedResults = results.slice(0, numResults).map((result: any, index: number) => {
      return `${index + 1}. ${result.title}\n   URL: ${result.url}\n   ${result.description}`;
    }).join('\n\n');

    return `Search results for "${query}":\n\n${formattedResults}`;
  }

  private async searchWithSerpAPI(query: string, numResults: number): Promise<string> {
    const response = await fetch(`https://serpapi.com/search.json?engine=google&q=${encodeURIComponent(query)}&num=${numResults}&api_key=${process.env.SERPAPI_KEY}`);

    if (!response.ok) {
      throw new Error(`SerpAPI error: ${response.status}`);
    }

    const data = await response.json();
    const results = data.organic_results || [];

    if (results.length === 0) {
      return `No results found for "${query}"`;
    }

    const formattedResults = results.slice(0, numResults).map((result: any, index: number) => {
      return `${index + 1}. ${result.title}\n   URL: ${result.link}\n   ${result.snippet || result.description || 'No description available'}`;
    }).join('\n\n');

    return `Search results for "${query}":\n\n${formattedResults}`;
  }

  private async searchWithTavily(query: string, numResults: number): Promise<string> {
    const response = await fetch('https://api.tavily.com/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        api_key: process.env.TAVILY_API_KEY,
        query: query,
        search_depth: 'advanced',
        include_answer: true,
        include_images: false,
        include_raw_content: false,
        max_results: numResults,
      }),
    });

    if (!response.ok) {
      throw new Error(`Tavily API error: ${response.status}`);
    }

    const data = await response.json();
    const results = data.results || [];

    if (results.length === 0) {
      return `No results found for "${query}"`;
    }

    const formattedResults = results.slice(0, numResults).map((result: any, index: number) => {
      return `${index + 1}. ${result.title}\n   URL: ${result.url}\n   ${result.content}`;
    }).join('\n\n');

    let searchResult = `Search results for "${query}":\n\n${formattedResults}`;

    if (data.answer) {
      searchResult = `AI Summary: ${data.answer}\n\n${searchResult}`;
    }

    return searchResult;
  }

  private mockSearch(query: string, numResults: number): string {
    console.log('⚠️  Using mock search results. Set up a real search API for better results.');

    const mockResults = [
      {
        title: `Mock Result 1 for "${query}"`,
        url: 'https://example.com/result1',
        description: 'This is a placeholder search result. To get real web search results, set up one of the supported search APIs (Brave, SerpAPI, or Tavily) in your environment variables.'
      },
      {
        title: `Mock Result 2 for "${query}"`,
        url: 'https://example.com/result2',
        description: 'Another placeholder result. Real search APIs provide current, relevant information from across the web.'
      },
      {
        title: `Mock Result 3 for "${query}"`,
        url: 'https://example.com/result3',
        description: 'Configure BRAVE_API_KEY, SERPAPI_KEY, or TAVILY_API_KEY to enable real web search functionality.'
      },
    ];

    const formattedResults = mockResults.slice(0, numResults).map((result, index) => {
      return `${index + 1}. ${result.title}\n   URL: ${result.url}\n   ${result.description}`;
    }).join('\n\n');

    return `🔍 Mock search results for "${query}":\n\n${formattedResults}\n\n💡 To get real search results, add an API key for Brave Search, SerpAPI, or Tavily to your environment.`;
  }
}

// Create and export the tool instance
export const webSearchTool = new WebSearchTool();
