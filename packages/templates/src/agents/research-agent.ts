import { AgentDefinition, AgentContext } from '@agent-platform/core';
import { webSearchTool, webScrapeTool } from '../tools/web-tools';

/**
 * Plan the research approach
 */
async function planResearch(
  query: string,
  context: AgentContext
): Promise<{ queries: string[]; approach: string }> {
  // Analyze query and break it down into searchable components
  const queries: string[] = [];

  // For now, use the original query
  // In a full implementation, you'd use an LLM to break down complex queries
  queries.push(query);

  // Add related queries for comprehensive research
  if (query.toLowerCase().includes('how')) {
    queries.push(`${query} step by step`);
  } else if (query.toLowerCase().includes('what')) {
    queries.push(`${query} explained`);
  } else if (query.toLowerCase().includes('best')) {
    queries.push(`${query} comparison`);
  }

  return {
    queries: queries.slice(0, 3), // Limit to 3 queries to avoid rate limits
    approach: 'multi-source search and synthesis',
  };
}

/**
 * Conduct web searches
 */
async function conductSearches(
  queries: string[],
  context: AgentContext
): Promise<Array<{ query: string; results: any[] }>> {
  const searchTool = context.tools.get('web-search');
  if (!searchTool) {
    throw new Error('Web search tool not available');
  }

  const allResults = [];

  for (const query of queries) {
    try {
      const result = await searchTool.execute({ query, maxResults: 5 }, context);
      allResults.push({
        query,
        results: result.results || [],
      });
    } catch (error) {
      context.emit?.('tool:error', {
        message: `Search failed for "${query}": ${error}`,
      });
    }
  }

  return allResults;
}

/**
 * Deep dive analysis by scraping key pages
 */
async function deepDiveAnalysis(
  searchResults: Array<{ query: string; results: any[] }>,
  context: AgentContext
): Promise<Array<{ url: string; content: string }>> {
  const scrapeTool = context.tools.get('web-scrape');
  if (!scrapeTool) {
    return [];
  }

  const deepContent = [];

  // Get top result from first search
  const topResults = searchResults[0]?.results.slice(0, 2) || [];

  for (const result of topResults) {
    try {
      const scraped = await scrapeTool.execute({ url: result.url }, context);
      deepContent.push({
        url: result.url,
        content: scraped.content,
      });
    } catch (error) {
      // Scraping failed, skip this URL
      context.emit?.('tool:error', {
        message: `Failed to scrape ${result.url}`,
      });
    }
  }

  return deepContent;
}

/**
 * Synthesize all findings into a comprehensive report
 */
async function synthesizeFindings(
  originalQuery: string,
  searchResults: Array<{ query: string; results: any[] }>,
  deepAnalysis: Array<{ url: string; content: string }>,
  context: AgentContext
): Promise<string> {
  // Build a comprehensive report
  let report = `# Research Report: ${originalQuery}\n\n`;

  report += `## Executive Summary\n\n`;
  report += `Based on research across multiple sources, here are the key findings:\n\n`;

  // Add search results
  for (const search of searchResults) {
    if (search.results.length > 0) {
      report += `### Findings for: "${search.query}"\n\n`;

      for (const result of search.results) {
        report += `**${result.title}**\n`;
        report += `${result.snippet}\n`;
        report += `Source: ${result.url}\n\n`;
      }
    }
  }

  // Add deep analysis if available
  if (deepAnalysis.length > 0) {
    report += `## Detailed Analysis\n\n`;

    for (const analysis of deepAnalysis) {
      report += `### Content from: ${analysis.url}\n\n`;
      // Include first 500 characters of scraped content
      const preview = analysis.content.substring(0, 500);
      report += `${preview}...\n\n`;
    }
  }

  report += `## Conclusion\n\n`;
  report += `This research provides comprehensive information about ${originalQuery}. `;
  report += `Review the sources above for detailed information.\n\n`;

  report += `---\n`;
  report += `*Research conducted by Agent Platform Research Agent*\n`;

  return report;
}

/**
 * Research Agent
 *
 * A powerful research assistant that can:
 * - Search the web for information
 * - Scrape and analyze web pages
 * - Synthesize information from multiple sources
 * - Provide well-structured, comprehensive answers
 *
 * Best for: Market research, competitive analysis, information gathering
 */
const researchAgent: AgentDefinition = {
  name: 'research-agent',
  version: '1.0.0',
  description: 'AI-powered research assistant that searches and analyzes web content',
  author: 'Agent Platform',
  tags: ['research', 'web-search', 'analysis'],

  systemPrompt: `You are an expert research assistant with access to web search and scraping tools.

Your capabilities:
- Search the web for relevant information
- Extract and analyze content from web pages
- Synthesize information from multiple sources
- Provide comprehensive, well-structured answers

Research Methodology:
1. Understand the research question thoroughly
2. Break down complex queries into searchable components
3. Search for information from multiple angles
4. Verify information across multiple sources
5. Synthesize findings into a coherent, well-structured response

Output Format:
- Start with a clear executive summary
- Use bullet points for key findings
- Include sources and citations
- Highlight important insights
- Be objective and fact-based

Quality Standards:
- Cite your sources
- Distinguish between facts and opinions
- Acknowledge uncertainties
- Provide context and nuance
- Be thorough but concise`,

  tools: ['web-search', 'web-scrape'],

  config: {
    model: 'claude-sonnet-4',
    provider: 'anthropic',
    temperature: 0.7,
    maxTokens: 4000,
  },

  async onInit(context: AgentContext) {
    // Register web tools
    if (!context.tools.has('web-search')) {
      context.tools.set('web-search', webSearchTool);
    }
    if (!context.tools.has('web-scrape')) {
      context.tools.set('web-scrape', webScrapeTool);
    }
  },

  async execute(input: string, context: AgentContext): Promise<string> {
    try {
      context.emit?.('agent:thinking', {
        message: 'Analyzing research query...',
      });

      // Step 1: Understand what we need to research
      const researchPlan = await planResearch(input, context);

      context.emit?.('agent:thinking', {
        message: 'Executing research plan...',
      });

      // Step 2: Execute searches
      const searchResults = await conductSearches(researchPlan.queries, context);

      context.emit?.('agent:thinking', {
        message: 'Analyzing findings...',
      });

      // Step 3: Optionally scrape key pages for deeper analysis
      const deepAnalysis = await deepDiveAnalysis(searchResults, context);

      context.emit?.('agent:thinking', {
        message: 'Synthesizing research...',
      });

      // Step 4: Synthesize findings
      const report = await synthesizeFindings(
        input,
        searchResults,
        deepAnalysis,
        context
      );

      return report;
    } catch (error) {
      context.emit?.('agent:error', {
        message: `Research failed: ${error}`,
      });

      return `I encountered an error while conducting research: ${error}\n\nPlease try rephrasing your query or check your internet connection.`;
    }
  },
};

export default researchAgent;
