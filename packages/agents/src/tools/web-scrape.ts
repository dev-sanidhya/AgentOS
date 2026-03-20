import axios from "axios";
import * as cheerio from "cheerio";
import { AgentTool } from "../types";

const MAX_CONTENT_LENGTH = 15000;

/**
 * Web scraping tool that extracts clean text content from web pages.
 */
export const webScrapeTool: AgentTool = {
  name: "web_scrape",
  description:
    "Fetch and extract the text content from a web page URL. Returns the main content of the page, cleaned of HTML tags, scripts, and styles. Use this after web_search to read full articles.",
  input_schema: {
    type: "object" as const,
    properties: {
      url: {
        type: "string",
        description: "The URL to scrape",
      },
      selector: {
        type: "string",
        description:
          "Optional CSS selector to target specific content (e.g., 'article', 'main', '.content')",
      },
    },
    required: ["url"],
  },
  async execute(input: Record<string, unknown>): Promise<string> {
    const url = input.url as string;
    const selector = input.selector as string | undefined;

    try {
      const response = await axios.get(url, {
        timeout: 15000,
        maxRedirects: 5,
        headers: {
          "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
          Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        responseType: "text",
      });

      const $ = cheerio.load(response.data);

      // Remove noise elements
      $("script, style, nav, footer, header, aside, iframe, noscript").remove();
      $('[role="navigation"], [role="banner"], [role="contentinfo"]').remove();
      $(".sidebar, .nav, .menu, .footer, .header, .ad, .advertisement").remove();

      // Extract content
      let content: string;

      if (selector) {
        content = $(selector).text();
      } else {
        // Try common content containers in priority order
        const selectors = ["article", "main", '[role="main"]', ".content", ".post", "#content"];
        let found = false;

        for (const sel of selectors) {
          const el = $(sel);
          if (el.length > 0 && el.text().trim().length > 100) {
            content = el.text();
            found = true;
            break;
          }
        }

        if (!found) {
          content = $("body").text();
        }
      }

      // Clean up whitespace
      content = content!
        .replace(/\s+/g, " ")
        .replace(/\n\s*\n/g, "\n\n")
        .trim();

      // Extract title
      const title = $("title").text().trim() || $("h1").first().text().trim();

      if (!content || content.length < 50) {
        return `Could not extract meaningful content from ${url}. The page may require JavaScript rendering.`;
      }

      // Truncate if too long
      if (content.length > MAX_CONTENT_LENGTH) {
        content = content.slice(0, MAX_CONTENT_LENGTH) + "\n\n[Content truncated...]";
      }

      return `**${title}**\nSource: ${url}\n\n${content}`;
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      return `Failed to scrape ${url}: ${message}`;
    }
  },
};
