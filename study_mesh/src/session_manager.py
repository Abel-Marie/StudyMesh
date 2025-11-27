from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import uuid

class SessionManager:
    """Manages ADK sessions for user interactions."""
    
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.app_name = "productivity_planner"
        self.active_sessions = {}
    
    async def create_session(self, user_id):
        """Create a new session for a user."""
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        self.active_sessions[user_id] = session_id
        return session_id
    
    async def get_or_create_session(self, user_id):
        """Get existing session or create new one."""
        if user_id in self.active_sessions:
            return self.active_sessions[user_id]
        return await self.create_session(user_id)
    
    def create_runner(self, agent, user_id=None):
        """Create a runner for an agent with session management."""
        return Runner(
            agent=agent,
            app_name=self.app_name,
            session_service=self.session_service
        )
    
    async def run_agent(self, agent, user_id, message):
        """Run an agent with session management."""
        session_id = await self.get_or_create_session(user_id)
        runner = self.create_runner(agent, user_id)
        
        # Create message content
        content = types.Content(parts=[types.Part(text=message)])
        
        # Run agent and collect response
        response_text = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text"):
                        response_text += part.text
        
        return response_text
    
    def run_agent_sync(self, agent, user_id, message):
        """Synchronous wrapper for run_agent that handles event loop properly."""
        import asyncio
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running (e.g., in Streamlit), create new loop
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(self.run_agent(agent, user_id, message))
            else:
                return loop.run_until_complete(self.run_agent(agent, user_id, message))
        except RuntimeError:
            # No event loop, create new one
            return asyncio.run(self.run_agent(agent, user_id, message))
