"""
Tools package for {{AgentName}} CrewAI implementation.

This package provides web search and scraping capabilities
optimized for CrewAI multi-agent research workflows.
"""

from .web_search import WebSearchTool
from .web_scrape import WebScrapeTool

__all__ = ['WebSearchTool', 'WebScrapeTool']

# Tool instances for easy import
web_search_tool = WebSearchTool()
web_scrape_tool = WebScrapeTool()