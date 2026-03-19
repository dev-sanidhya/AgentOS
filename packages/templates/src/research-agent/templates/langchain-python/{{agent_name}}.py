"""
{{AgentName}} - AI Research Assistant

This agent uses web search and content scraping to gather and synthesize
information from multiple sources.

Built with LangChain for flexible, composable AI workflows.
"""

from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage
import os
from dotenv import load_dotenv

from .tools.web_search import web_search_tool
from .tools.web_scrape import web_scrape_tool
from .prompts import RESEARCH_AGENT_PROMPT

load_dotenv()


class {{AgentName}}:
    """
    AI-powered research agent that searches the web and analyzes content.

    Features:
    - Multi-source web search
    - Content extraction and scraping
    - Information synthesis
    - Comprehensive report generation

    Usage:
        agent = {{AgentName}}()
        result = agent.research("AI trends in 2026")
        print(result)
    """

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_iterations: int = 10,
        verbose: bool = False
    ):
        """
        Initialize the research agent.

        Args:
            model: LLM model to use (gpt-4, gpt-3.5-turbo, claude-3-opus, etc.)
            temperature: Creativity level (0-1)
            max_iterations: Maximum agent iterations
            verbose: Enable detailed logging
        """
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.verbose = verbose

        # Initialize LLM
        self.llm = self._create_llm()

        # Initialize tools
        self.tools = [
            web_search_tool,
            web_scrape_tool,
        ]

        # Create agent
        self.agent = self._create_agent()

    def _create_llm(self):
        """Create the language model instance."""
        if "gpt" in self.model.lower():
            return ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        elif "claude" in self.model.lower():
            return ChatAnthropic(
                model=self.model,
                temperature=self.temperature,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            raise ValueError(f"Unsupported model: {self.model}")

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent executor."""
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", RESEARCH_AGENT_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        # Create executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            max_iterations=self.max_iterations,
            verbose=self.verbose,
            return_intermediate_steps=True
        )

    def research(self, query: str, chat_history: List[BaseMessage] = None) -> Dict[str, Any]:
        """
        Conduct research on the given query.

        Args:
            query: Research question or topic
            chat_history: Optional conversation history

        Returns:
            Dictionary containing:
            - output: Research results
            - intermediate_steps: Tool calls and results
        """
        result = self.agent.invoke({
            "input": query,
            "chat_history": chat_history or []
        })

        return {
            "output": result["output"],
            "intermediate_steps": result.get("intermediate_steps", []),
            "input": query
        }

    async def aresearch(self, query: str, chat_history: List[BaseMessage] = None) -> Dict[str, Any]:
        """
        Async version of research method.

        Args:
            query: Research question or topic
            chat_history: Optional conversation history

        Returns:
            Dictionary containing research results
        """
        result = await self.agent.ainvoke({
            "input": query,
            "chat_history": chat_history or []
        })

        return {
            "output": result["output"],
            "intermediate_steps": result.get("intermediate_steps", []),
            "input": query
        }


# Convenience function for quick usage
def research(query: str, model: str = "gpt-4", verbose: bool = False) -> str:
    """
    Quick research function.

    Args:
        query: Research question
        model: LLM model to use
        verbose: Enable logging

    Returns:
        Research results as string
    """
    agent = {{AgentName}}(model=model, verbose=verbose)
    result = agent.research(query)
    return result["output"]
