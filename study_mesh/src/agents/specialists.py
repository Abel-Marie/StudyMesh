import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from google.adk.tools.function_tool import FunctionTool
from google.adk.tools import google_search, AgentTool, ToolContext
from google.adk.code_executors import BuiltInCodeExecutor

from src.config import get_retry_config
import datetime

load_dotenv()


# --- Custom Tool Definitions ---

def get_current_datetime():
    """Returns the current date and time to help with planning schedules."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fetch_user_calendar(days_ahead: int = 7):
    """Fetches the user's existing calendar events to avoid scheduling conflicts."""
    # Simulation of a calendar API call
    return f"User has 'Math Class' every day at 10 AM. Free mostly on weekends."

def fetch_arxiv_abstract(query: str):
    """Searches Arxiv specifically for academic paper abstracts."""
    return f"Found abstract for '{query}': Recent advances in AI productivity..."

def get_study_logs(user_id: str):
    """Retrieves the raw study session logs for the user (time spent, tasks completed)."""
    return "Mon: 2hrs (Math), Tue: 1hr (History), Wed: 0hrs (Missed)."

def validate_post_length(content: str, platform: str):
    """Checks if the content fits within the character limits of the platform."""
    limits = {"twitter": 280, "linkedin": 3000}
    limit = limits.get(platform.lower(), 1000)
    if len(content) > limit:
        return f"Error: Content is {len(content)} chars; limit is {limit}."
    return "Length OK."

# --- Agent Definitions ---

def create_task_planner_agent():
    """Agent specialized in analyzing goals and creating task roadmaps."""
    return LlmAgent(
        model=Gemini(
            model="gemini-2.5-flash-lite", 
            api_key=os.environ.get("GOOGLE_API_KEY"), 
            retry_options=get_retry_config()
        ),
        name="task_planner",
        description="Analyzes user goals and creates personalized task roadmaps",
        instruction="""You are a task planning specialist.
        
        Your job:
        1. Check the current date and user's existing calendar.
        2. Analyze the user's study goals and available time.
        3. Break down goals into daily, weekly, and long-term tasks.
        4. Estimate time for each task.
        
        ALWAYS use your tools to check the date and availability before planning.
        """,
        tools=[
            # Custom tools to give context
            FunctionTool(get_current_datetime),
            FunctionTool(fetch_user_calendar)
        ]
    )

def create_research_agent():
    """Agent specialized in finding and summarizing research papers."""
    return LlmAgent(
        model=Gemini(
            model="gemini-2.5-flash-lite", 
            api_key=os.environ.get("GOOGLE_API_KEY"), 
            retry_options=get_retry_config()
        ),
        name="research_agent",
        description="Finds relevant research papers and creates summaries",
        instruction="""You are a research paper specialist.
        
        Your job:
        1. Search for relevant papers using Google Search or Arxiv.
        2. Filter papers by relevance and recency (last 6 months).
        3. Create concise, student-friendly summaries.
        
        Use GoogleSearch for broad topics and Arxiv tool for specific technical papers.
        """,
        tools=[
            # Built-in ADK tool for web access
            google_search, 
            # Custom tool for academic database
            FunctionTool(fetch_arxiv_abstract)
        ]
    )

def create_progress_analyst_agent():
    """Agent specialized in analyzing progress and generating insights."""
    return LlmAgent(
        model=Gemini(
            model="gemini-2.5-flash-lite", 
            api_key=os.environ.get("GOOGLE_API_KEY"), 
            retry_options=get_retry_config()
        ),
        name="progress_analyst",
        description="Analyzes user progress and provides insights",
        instruction="""You are a progress analysis specialist.
        
        Your job:
        1. Retrieve the user's study logs.
        2. Use the CodeInterpreter to calculate completion rates and visualize trends.
        3. Identify blockers (e.g., days with 0 hours).
        4. Generate encouraging but honest feedback.
        
        Use CodeInterpreter to perform mathematical analysis on the study log data.
        """,
        tools=[
            # Built-in ADK tool for data analysis
            # CodeInterpreter(), # Removed as not found
            # Custom tool to get the raw data
            FunctionTool(get_study_logs)
        ]
    )

def create_content_creator_agent():
    """Agent specialized in creating social media content."""
    return LlmAgent(
        model=Gemini(
            model="gemini-2.5-flash-lite", 
            api_key=os.environ.get("GOOGLE_API_KEY"), 
            retry_options=get_retry_config()
        ),
        name="content_creator",
        description="Creates engaging social media posts about achievements",
        instruction="""You are a social media content specialist.
        
        Your job:
        1. Transform achievements into engaging posts.
        2. Search for currently trending hashtags related to the topic.
        3. Adapt tone for different platforms (LinkedIn, Twitter).
        4. Validate that your post fits the character limit.
        
        Always validate the post length before finalizing.
        """,
        tools=[
            # Built-in tool to find trends
            google_search,
            # Custom tool to ensure quality
            FunctionTool(validate_post_length)
        ]
    )