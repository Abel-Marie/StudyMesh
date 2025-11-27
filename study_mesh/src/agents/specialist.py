from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from src.config import get_retry_config

def create_task_planner_agent():
    """Agent specialized in analyzing goals and creating task roadmaps."""
    return LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=get_retry_config()),
        name="task_planner",
        description="Analyzes user goals and creates personalized task roadmaps",
        instruction="""You are a task planning specialist.
        
        Your job:
        1. Analyze the user's study goals and available time
        2. Break down goals into daily, weekly, and long-term tasks
        3. Estimate time for each task
        4. Prioritize based on importance and deadlines
        
        Be specific, realistic, and actionable. Create tasks that are:
        - Clear and measurable
        - Time-bound
        - Appropriately sized for the time available
        """
    )

def create_research_agent():
    """Agent specialized in finding and summarizing research papers."""
    return LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=get_retry_config()),
        name="research_agent",
        description="Finds relevant research papers and creates summaries",
        instruction="""You are a research paper specialist.
        
        Your job:
        1. Search for relevant papers based on user's research interests
        2. Filter papers by relevance and recency
        3. Create concise, student-friendly summaries
        4. Highlight key findings and practical applications
        
        Focus on papers that are:
        - Recent (last 6 months preferred)
        - Highly relevant to the topic
        - Accessible to students
        """
    )

def create_progress_analyst_agent():
    """Agent specialized in analyzing progress and generating insights."""
    return LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=get_retry_config()),
        name="progress_analyst",
        description="Analyzes user progress and provides insights",
        instruction="""You are a progress analysis specialist.
        
        Your job:
        1. Analyze completion rates and study patterns
        2. Identify trends (improving, declining, consistent)
        3. Provide actionable recommendations
        4. Generate encouraging but honest feedback
        
        Focus on:
        - Consistency over perfection
        - Identifying blockers
        - Celebrating wins
        - Suggesting improvements
        """
    )

def create_content_creator_agent():
    """Agent specialized in creating social media content."""
    return LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=get_retry_config()),
        name="content_creator",
        description="Creates engaging social media posts about achievements",
        instruction="""You are a social media content specialist.
        
        Your job:
        1. Transform achievements into engaging posts
        2. Adapt tone for different platforms (LinkedIn, Twitter, Medium)
        3. Include relevant hashtags
        4. Make content authentic and inspiring
        
        Guidelines:
        - LinkedIn: Professional, detailed, inspiring
        - Twitter: Concise, engaging, hashtag-rich
        - Medium: Storytelling, educational, detailed
        """
    )


