import { Tool, AgentContext } from '@agent-platform/core';
import axios from 'axios';
import * as cheerio from 'cheerio';
import { z } from 'zod';

/**
 * Web Search Tool
 * Searches the web using a search API (you can integrate with Brave, Google, or other providers)
 */
export const webSearchTool: Tool = {
  name: 'web-search',
  description: 'Search the web for information on a given query',
  parameters: z.object({
    query: z.string().describe('The search query'),
    maxResults: z.number().optional().default(5).describe('Maximum number of results to return'),
  }),

  async execute(params: { query: string; maxResults?: number }, context: AgentContext) {
    const { query, maxResults = 5 } = params;

    try {
      // This is a placeholder - in production, you'd integrate with:
      // - Brave Search API
      // - Google Custom Search
      // - Bing Search API
      // - SerpAPI, etc.

      // For now, we'll return a structured response format
      context.emit?.('tool:log', {
        message: `Searching for: "${query}"`,
      });

      // Simulated search results (replace with real API integration)
      const results = [
        {
          title: `Search result for: ${query}`,
          url: `https://example.com/search?q=${encodeURIComponent(query)}`,
          snippet: `This is a placeholder result for "${query}". Integrate a real search API for production use.`,
        },
      ];

      return {
        query,
        results: results.slice(0, maxResults),
        totalResults: results.length,
      };
    } catch (error) {
      throw new Error(`Web search failed: ${error}`);
    }
  },
};

/**
 * Web Scrape Tool
 * Fetches and extracts text content from a web page
 */
export const webScrapeTool: Tool = {
  name: 'web-scrape',
  description: 'Fetch and extract text content from a web page',
  parameters: z.object({
    url: z.string().url().describe('The URL to scrape'),
    selector: z.string().optional().describe('CSS selector to extract specific content'),
  }),

  async execute(params: { url: string; selector?: string }, context: AgentContext) {
    const { url, selector } = params;

    try {
      context.emit?.('tool:log', {
        message: `Scraping URL: ${url}`,
      });

      // Fetch the page
      const response = await axios.get(url, {
        headers: {
          'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
        timeout: 10000, // 10 second timeout
      });

      // Parse HTML
      const $ = cheerio.load(response.data);

      // Remove script and style elements
      $('script, style').remove();

      let content: string;

      if (selector) {
        // Extract specific content with selector
        content = $(selector).text().trim();
      } else {
        // Extract main text content
        content = $('body').text().trim();
      }

      // Clean up whitespace
      content = content.replace(/\s+/g, ' ').trim();

      // Limit content length
      const maxLength = 10000;
      if (content.length > maxLength) {
        content = content.substring(0, maxLength) + '...';
      }

      return {
        url,
        content,
        length: content.length,
        title: $('title').text().trim(),
      };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to scrape ${url}: ${error.message}`);
      }
      throw new Error(`Web scraping failed: ${error}`);
    }
  },
};

/**
 * HTTP Request Tool
 * Make HTTP requests to APIs
 */
export const httpRequestTool: Tool = {
  name: 'http-request',
  description: 'Make HTTP requests to external APIs',
  parameters: z.object({
    url: z.string().url().describe('The URL to request'),
    method: z.enum(['GET', 'POST', 'PUT', 'DELETE', 'PATCH']).default('GET'),
    headers: z.record(z.string()).optional().describe('Request headers'),
    body: z.any().optional().describe('Request body for POST/PUT/PATCH'),
  }),

  async execute(
    params: {
      url: string;
      method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
      headers?: Record<string, string>;
      body?: any;
    },
    context: AgentContext
  ) {
    const { url, method = 'GET', headers, body } = params;

    try {
      context.emit?.('tool:log', {
        message: `Making ${method} request to: ${url}`,
      });

      const response = await axios({
        url,
        method,
        headers,
        data: body,
        timeout: 30000, // 30 second timeout
      });

      return {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
        data: response.data,
      };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          status: error.response?.status,
          statusText: error.response?.statusText,
          error: error.message,
          data: error.response?.data,
        };
      }
      throw new Error(`HTTP request failed: ${error}`);
    }
  },
};
