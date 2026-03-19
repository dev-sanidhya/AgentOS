"""
{{AgentName}} - CrewAI Implementation

A research crew built with CrewAI that coordinates multiple specialized agents
to conduct comprehensive research and analysis.
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()


class {{AgentName}}:
    """
    Research crew that uses specialized agents to gather and analyze information.

    The crew consists of:
    - Researcher: Searches for information
    - Analyst: Analyzes and synthesizes findings
    - Writer: Creates comprehensive reports
    """

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        verbose: bool = True,
        max_iterations: int = 5
    ):
        self.model = model
        self.temperature = temperature
        self.verbose = verbose
        self.max_iterations = max_iterations
        self.llm = self._create_llm()
        self.tools = self._setup_tools()
        self.crew = self._create_crew()

    def _create_llm(self):
        """Initialize the language model."""
        if self.model.startswith("claude"):
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            return ChatAnthropic(
                model=self.model,
                temperature=self.temperature,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY not found in environment")
            return ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )

    def _setup_tools(self):
        """Initialize research tools."""
        tools = []

        # Web search tool (requires SERPER_API_KEY)
        if os.getenv("SERPER_API_KEY"):
            search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))
            tools.append(search_tool)

        # Web scraping tool
        scrape_tool = ScrapeWebsiteTool()
        tools.append(scrape_tool)

        return tools

    def _create_researcher_agent(self):
        """Create the researcher agent."""
        return Agent(
            role='Senior Research Specialist',
            goal='Find the most relevant and up-to-date information on any given topic',
            backstory="""You are an expert at finding information online. You know how to search effectively,
            identify reliable sources, and gather comprehensive data on any topic. You're particularly good at
            finding recent developments and authoritative sources.""",
            verbose=self.verbose,
            allow_delegation=True,
            tools=self.tools,
            llm=self.llm,
            max_iter=self.max_iterations
        )

    def _create_analyst_agent(self):
        """Create the analyst agent."""
        return Agent(
            role='Data Analysis Expert',
            goal='Analyze and synthesize information to extract key insights',
            backstory="""You are a skilled analyst who excels at processing large amounts of information
            and identifying patterns, trends, and key insights. You can distill complex information into
            clear, actionable insights and identify what's most important.""",
            verbose=self.verbose,
            allow_delegation=True,
            llm=self.llm,
            max_iter=self.max_iterations
        )

    def _create_writer_agent(self):
        """Create the writer agent."""
        return Agent(
            role='Research Report Writer',
            goal='Create comprehensive, well-structured research reports',
            backstory="""You are an expert writer who specializes in creating clear, comprehensive reports.
            You know how to organize information logically, write engaging content, and present complex
            information in an accessible way. You always cite sources and maintain academic standards.""",
            verbose=self.verbose,
            allow_delegation=False,
            llm=self.llm,
            max_iter=self.max_iterations
        )

    def _create_crew(self):
        """Create the research crew."""
        # Create agents
        researcher = self._create_researcher_agent()
        analyst = self._create_analyst_agent()
        writer = self._create_writer_agent()

        return Crew(
            agents=[researcher, analyst, writer],
            process=Process.sequential,
            verbose=self.verbose
        )

    def research(self, query: str) -> Dict[str, Any]:
        """
        Conduct research on the given query.

        Args:
            query (str): Research question or topic

        Returns:
            Dict containing the research results and metadata
        """
        if self.verbose:
            print(f"🔍 Starting research crew for: {query}")

        # Define research tasks
        research_task = Task(
            description=f"""
            Conduct comprehensive research on: {query}

            Your job is to:
            1. Search for the most recent and relevant information
            2. Identify authoritative sources
            3. Gather data from multiple perspectives
            4. Find specific facts, statistics, and examples
            5. Look for expert opinions and analysis

            Focus on finding high-quality, credible sources and current information.
            """,
            agent=self.crew.agents[0],  # Researcher
            expected_output="Detailed research findings with sources and key data points"
        )

        analysis_task = Task(
            description=f"""
            Analyze the research findings for: {query}

            Your job is to:
            1. Review all the research data collected
            2. Identify key themes and patterns
            3. Extract the most important insights
            4. Note any conflicting information or gaps
            5. Prioritize information by importance and reliability

            Provide a structured analysis that highlights what's most important.
            """,
            agent=self.crew.agents[1],  # Analyst
            expected_output="Structured analysis with key insights and prioritized findings"
        )

        writing_task = Task(
            description=f"""
            Create a comprehensive research report on: {query}

            Your job is to:
            1. Synthesize all research and analysis into a cohesive report
            2. Structure the information logically
            3. Write clear, engaging content
            4. Include proper citations and source references
            5. Provide an executive summary

            Format the report with clear sections and professional presentation.
            """,
            agent=self.crew.agents[2],  # Writer
            expected_output="Complete research report with executive summary, findings, and citations"
        )

        # Execute the crew
        try:
            result = self.crew.kickoff(
                tasks=[research_task, analysis_task, writing_task]
            )

            return {
                "query": query,
                "output": result,
                "agents_used": [agent.role for agent in self.crew.agents],
                "tasks_completed": len([research_task, analysis_task, writing_task]),
                "success": True
            }

        except Exception as e:
            if self.verbose:
                print(f"❌ Research crew failed: {e}")

            return {
                "query": query,
                "output": f"Research failed: {str(e)}",
                "error": str(e),
                "success": False
            }


def research(
    query: str,
    model: str = "gpt-4",
    temperature: float = 0.7,
    verbose: bool = True
) -> str:
    """
    Quick research function using the crew.

    Args:
        query: Research question
        model: LLM model to use
        temperature: Creativity level (0-1)
        verbose: Enable detailed logging

    Returns:
        Research report as string
    """
    crew = {{AgentName}}(
        model=model,
        temperature=temperature,
        verbose=verbose
    )

    result = crew.research(query)
    return result["output"]


if __name__ == "__main__":
    # Example usage
    crew = {{AgentName}}(verbose=True)
    result = crew.research("What are the latest trends in artificial intelligence?")
    print("\n" + "="*50)
    print("RESEARCH RESULTS")
    print("="*50)
    print(result["output"])