import logging
import os
from datetime import datetime

class Logger:
    """Centralized logging for the planner."""
    
    def __init__(self, log_file="planner.log"):
        self.log_file = log_file
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging to file and console."""
        # Remove existing log file
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("ProductivityPlanner")
        self.logger.info("Logging initialized")
    
    def log_agent_call(self, agent_name, message):
        """Log an agent call."""
        self.logger.info(f"Agent Call: {agent_name} - {message[:100]}...")
    
    def log_task_completion(self, task_id, task_title):
        """Log task completion."""
        self.logger.info(f"Task Completed: {task_id} - {task_title}")
    
    def log_error(self, error_type, error_message):
        """Log an error."""
        self.logger.error(f"{error_type}: {error_message}")
    
    def log_user_action(self, user_id, action):
        """Log user action."""
        self.logger.info(f"User Action: {user_id} - {action}")
    
    def get_recent_logs(self, lines=50):
        """Get recent log entries."""
        if not os.path.exists(self.log_file):
            return []
        
        with open(self.log_file, 'r') as f:
            all_lines = f.readlines()
            return all_lines[-lines:]
