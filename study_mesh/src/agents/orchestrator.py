import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
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

load_dotenv()

def create_research_squad_agent():
    """
    Creates a ParallelAgent that runs research and deadline parsing simultaneously.
    Useful when gathering information where one task implies the other but they don't strictly depend on order.
    """
    research_agent = create_research_agent()
    deadline_parser = create_deadline_parser_agent()
    
    return ParallelAgent(
        name="research_squad",
        description="Executes research and deadline extraction in parallel for efficiency.",
        sub_agents=[research_agent, deadline_parser]
    )

def create_content_pipeline_agent():
    """
    Creates a SequentialAgent that enforces a strict dependency:
    1. Analyze progress/data
    2. Create content based on that analysis
    """
    progress_analyst = create_progress_analyst_agent()
    content_creator = create_content_creator_agent()
    
    return SequentialAgent(
        name="content_pipeline",
        description="Sequentially analyzes progress and then generates content based on the insights.",
        sub_agents=[progress_analyst, content_creator]
    )

def create_orchestrator_agent():
    """Main orchestrator agent that coordinates all specialist agents and workflows."""
    
    # Create individual specialists (for granular control if needed)
    task_planner = create_task_planner_agent()
    
    # Create composite workflow agents (Helper functions used here)
    research_squad = create_research_squad_agent()
    content_pipeline = create_content_pipeline_agent()
    
    # Create orchestrator with specialists and workflows as tools
    orchestrator = LlmAgent(
        model=Gemini(
            model="gemini-2.5-flash-lite", 
            api_key=os.environ.get("GOOGLE_API_KEY"), 
            retry_options=get_retry_config()
        ),
        name="productivity_orchestrator",
        description="Main coordinator for the AI Productivity Planner",
        instruction="""You are the main productivity orchestrator.
        
        You coordinate a team of specialist agents and optimized workflows:
        
        **Individual Specialists:**
        - task_planner: Creates roadmaps and tasks
        
        **Optimized Workflows (Use these for efficiency):**
        - research_squad (Parallel): Use this when you need to find papers/info AND extract deadlines. It runs both specialists simultaneously.
        - content_pipeline (Sequential): Use this when the user needs a status update or social post. It ensures progress is analyzed BEFORE content is created.
        
        Your job:
        1. Understand user requests.
        2. Decide whether to call a single specialist or an optimized workflow.
        3. Delegate to the appropriate tool.
        4. Provide cohesive, helpful responses.
        """,
        tools=[
            # Single Agent Tool
            AgentTool(agent=task_planner),
            
            # Workflow Tools (Parallel & Sequential)
            AgentTool(agent=research_squad),
            AgentTool(agent=content_pipeline)
        ]
    )
    
    return orchestrator