from google.adk.memory import MemoryService
from datetime import datetime
import json

class MemoryManager:
    """Manages long-term memory for user patterns and preferences."""
    
    def __init__(self):
        self.memory_service = MemoryService()
        self.user_memories = {}
    
    def save_user_pattern(self, user_id, pattern_type, data):
        """Save a user pattern to memory."""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = {}
        
        if pattern_type not in self.user_memories[user_id]:
            self.user_memories[user_id][pattern_type] = []
        
        self.user_memories[user_id][pattern_type].append({
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    
    def get_user_patterns(self, user_id, pattern_type=None):
        """Retrieve user patterns from memory."""
        if user_id not in self.user_memories:
            return []
        
        if pattern_type:
            return self.user_memories[user_id].get(pattern_type, [])
        
        return self.user_memories[user_id]
    
    def analyze_study_patterns(self, user_id):
        """Analyze user's study patterns."""
        patterns = self.get_user_patterns(user_id, "study_sessions")
        
        if not patterns:
            return None
        
        # Calculate average study time
        total_hours = sum([p['data'].get('hours', 0) for p in patterns])
        avg_hours = total_hours / len(patterns)
        
        # Find most productive time
        time_distribution = {}
        for p in patterns:
            time_slot = p['data'].get('time_slot', 'unknown')
            time_distribution[time_slot] = time_distribution.get(time_slot, 0) + 1
        
        most_productive = max(time_distribution.items(), key=lambda x: x[1])[0] if time_distribution else None
        
        return {
            "avg_hours_per_session": avg_hours,
            "total_sessions": len(patterns),
            "most_productive_time": most_productive,
            "consistency_score": min(100, (len(patterns) / 30) * 100)  # Based on 30-day target
        }
    
    def get_recommendations(self, user_id):
        """Get personalized recommendations based on memory."""
        analysis = self.analyze_study_patterns(user_id)
        
        if not analysis:
            return ["Start tracking your study sessions to get personalized recommendations!"]
        
        recommendations = []
        
        if analysis['avg_hours_per_session'] < 1:
            recommendations.append("Try to increase your study session length to at least 1 hour for better focus.")
        
        if analysis['consistency_score'] < 50:
            recommendations.append("Focus on building consistency. Try to study at least 15 days per month.")
        
        if analysis['most_productive_time']:
            recommendations.append(f"You're most productive during {analysis['most_productive_time']}. Schedule important tasks then!")
        
        return recommendations if recommendations else ["Great job! Keep up the consistent work!"]
