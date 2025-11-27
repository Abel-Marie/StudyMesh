from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.agent_tool import AgentTool
from src.config import get_retry_config
from .specialists import (
    create_task_planner_agent,
    create_research_agent,
    create_progress_analyst_agent,
    create_content_creator_agent
)
from .deadline_parser import create_deadline_parser_agent

def create_orchestrator_agent():
    """Main orchestrator agent that coordinates all specialist agents."""
    
    # Create specialist agents
    task_planner = create_task_planner_agent()
    research_agent = create_research_agent()
    progress_analyst = create_progress_analyst_agent()
    content_creator = create_content_creator_agent()
    deadline_parser = create_deadline_parser_agent()
    
    # Create orchestrator with all specialists as sub-agents
    orchestrator = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=get_retry_config()),
        name="productivity_orchestrator",
        description="Main coordinator for the AI Productivity Planner",
        instruction="""You are the main productivity orchestrator.
        
        You coordinate a team of specialist agents:
        - task_planner: Creates roadmaps and tasks
        - research_agent: Finds and summarizes papers
        - progress_analyst: Analyzes progress and provides insights
        - content_creator: Generates social media posts
        - deadline_parser: Extracts deadline info from URLs and text
        
        Your job:
        1. Understand user requests
        2. Delegate to appropriate specialist agents
        3. Combine results from multiple agents when needed
        4. Provide cohesive, helpful responses
        
        Use parallel execution when tasks are independent.
        Use sequential execution when tasks depend on each other.
        """,
        tools=[
            AgentTool(agent=task_planner),
            AgentTool(agent=research_agent),
            AgentTool(agent=progress_analyst),
            AgentTool(agent=content_creator),
            AgentTool(agent=deadline_parser)
        ]
    )
    
    return orchestrator
