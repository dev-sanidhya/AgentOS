import { Tool } from '@langchain/core/tools';
import { z } from 'zod';
import { JSDOM } from 'jsdom';

// Input schema for the web scraping tool
const WebScrapeSchema = z.object({
  url: z.string().url().describe('URL of the webpage to scrape'),
  selector: z.string().optional().describe('CSS selector to extract specific content (optional)'),
});

export class WebScrapeTool extends Tool {
  name = 'web_scrape';
  description = 'Scrape and extract text content from any web page. Optionally use CSS selectors to target specific content.';
  schema = WebScrapeSchema;

  constructor() {
    super();
  }

  async _call(input: z.infer<typeof WebScrapeSchema>): Promise<string> {
    const { url, selector } = input;

    try {
      // Validate URL
      new URL(url);

      // Fetch the webpage
      const response = await fetch(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Accept-Encoding': 'gzip, deflate',
          'Cache-Control': 'no-cache',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const html = await response.text();
      
      // Parse HTML using JSDOM
      const dom = new JSDOM(html);
      const document = dom.window.document;

      let content: string;

      if (selector) {
        // Extract content using CSS selector
        const elements = document.querySelectorAll(selector);
        if (elements.length === 0) {
          return `No content found with selector "${selector}" on ${url}`;
        }
        
        content = Array.from(elements)
          .map(el => el.textContent?.trim())
          .filter(text => text && text.length > 0)
          .join('\n\n');
      } else {
        // Remove scripts, styles, and other non-content elements
        const excludeSelectors = [
          'script', 'style', 'nav', 'header', 'footer', 
          '.advertisement', '.ad', '.sidebar', '.menu',
          '[style*="display: none"]', '[style*="visibility: hidden"]'
        ];
        
        excludeSelectors.forEach(sel => {
          const elements = document.querySelectorAll(sel);
          elements.forEach(el => el.remove());
        });

        // Try to find the main content
        const contentSelectors = [
          'main', 'article', '[role="main"]', '.content', 
          '#content', '.post', '.article', 'body'
        ];

        let contentElement = null;
        for (const sel of contentSelectors) {
          contentElement = document.querySelector(sel);
          if (contentElement) break;
        }

        if (!contentElement) {
          contentElement = document.body;
        }

        content = contentElement?.textContent || '';
      }

      // Clean up the content
      content = this.cleanText(content);

      if (!content || content.length < 50) {
        return `Unable to extract meaningful content from ${url}. The page might be JavaScript-heavy or have restricted access.`;
      }

      // Limit content length to avoid token overflow
      const maxLength = 4000;
      if (content.length > maxLength) {
        content = content.substring(0, maxLength) + '\n\n[Content truncated...]';
      }

      return `Content from ${url}:\n\n${content}`;

    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        return `Failed to fetch ${url}: Network error or invalid URL`;
      }
      return `Error scraping ${url}: ${error instanceof Error ? error.message : String(error)}`;
    }
  }

  private cleanText(text: string): string {
    return text
      // Remove extra whitespace
      .replace(/\s+/g, ' ')
      // Remove multiple consecutive line breaks
      .replace(/\n\s*\n\s*\n/g, '\n\n')
      // Trim each line
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0)
      .join('\n')
      // Final trim
      .trim();
  }
}

// Create and export the tool instance
export const webScrapeTool = new WebScrapeTool();
