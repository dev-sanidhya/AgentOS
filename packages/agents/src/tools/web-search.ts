import axios from "axios";
import { AgentTool } from "../types";

/**
 * Web search tool using Brave Search API.
 *
 * Requires BRAVE_SEARCH_API_KEY environment variable,
 * or falls back to basic web scraping of search results.
 */
export const webSearchTool: AgentTool = {
  name: "web_search",
  description:
    "Search the web for information. Returns a list of results with titles, URLs, and snippets. Use this to find current information, research topics, or verify facts.",
  input_schema: {
    type: "object" as const,
    properties: {
      query: {
        type: "string",
        description: "The search query",
      },
      max_results: {
        type: "number",
        description: "Maximum number of results to return (default: 5)",
      },
    },
    required: ["query"],
  },
  async execute(input: Record<string, unknown>): Promise<string> {
    const query = input.query as string;
    const maxResults = (input.max_results as number) ?? 5;

    const braveKey = process.env.BRAVE_SEARCH_API_KEY;

    if (braveKey) {
      return searchWithBrave(query, maxResults, braveKey);
    }

    // Fallback: use DuckDuckGo instant answer API (limited but free, no key needed)
    return searchWithDDG(query, maxResults);
  },
};

async function searchWithBrave(
  query: string,
  maxResults: number,
  apiKey: string
): Promise<string> {
  const response = await axios.get("https://api.search.brave.com/res/v1/web/search", {
    params: { q: query, count: maxResults },
    headers: {
      Accept: "application/json",
      "Accept-Encoding": "gzip",
      "X-Subscription-Token": apiKey,
    },
    timeout: 10000,
  });

  const results = response.data.web?.results ?? [];

  if (results.length === 0) {
    return `No results found for "${query}".`;
  }

  const formatted = results
    .slice(0, maxResults)
    .map(
      (r: { title: string; url: string; description: string }, i: number) =>
        `${i + 1}. **${r.title}**\n   URL: ${r.url}\n   ${r.description}`
    )
    .join("\n\n");

  return `Search results for "${query}":\n\n${formatted}`;
}

async function searchWithDDG(query: string, maxResults: number): Promise<string> {
  try {
    const response = await axios.get("https://api.duckduckgo.com/", {
      params: {
        q: query,
        format: "json",
        no_redirect: 1,
        no_html: 1,
      },
      timeout: 10000,
    });

    const data = response.data;
    const results: string[] = [];

    // Abstract (main answer)
    if (data.Abstract) {
      results.push(`**Summary**: ${data.Abstract}\nSource: ${data.AbstractURL}`);
    }

    // Related topics
    if (data.RelatedTopics) {
      for (const topic of data.RelatedTopics.slice(0, maxResults)) {
        if (topic.Text && topic.FirstURL) {
          results.push(`- ${topic.Text}\n  URL: ${topic.FirstURL}`);
        }
      }
    }

    if (results.length === 0) {
      return `No results found for "${query}". Try a more specific search query or ensure BRAVE_SEARCH_API_KEY is set for better results.`;
    }

    return `Search results for "${query}":\n\n${results.join("\n\n")}`;
  } catch {
    return `Search failed for "${query}". Set BRAVE_SEARCH_API_KEY for reliable search results.`;
  }
}
