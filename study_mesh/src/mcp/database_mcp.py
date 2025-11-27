from database.db_manager import DatabaseManager
from datetime import datetime, timedelta

class DatabaseMCP:
    """MCP server for database queries and analytics."""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def query_progress_summary(self, days=7):
        """Get progress summary for the last N days."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        progress = self.db.get_progress(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        total_hours = sum([p['study_hours'] for p in progress if p['study_hours']])
        
        return {
            "period": f"{start_date} to {end_date}",
            "total_hours": total_hours,
            "avg_hours_per_day": total_hours / days,
            "sessions": len(progress)
        }
    
    def query_task_statistics(self):
        """Get task statistics."""
        all_tasks = self.db.get_tasks()
        
        stats = {
            "total": len(all_tasks),
            "completed": len([t for t in all_tasks if t['status'] == 'completed']),
            "pending": len([t for t in all_tasks if t['status'] == 'pending']),
            "in_progress": len([t for t in all_tasks if t['status'] == 'in_progress']),
            "by_type": {}
        }
        
        for task_type in ['daily', 'weekly', 'long-term']:
            type_tasks = [t for t in all_tasks if t['task_type'] == task_type]
            stats['by_type'][task_type] = {
                "total": len(type_tasks),
                "completed": len([t for t in type_tasks if t['status'] == 'completed'])
            }
        
        return stats
    
    def query_upcoming_deadlines(self, days=30):
        """Get upcoming deadlines."""
        deadlines = self.db.get_deadlines(status="pending")
        
        upcoming = []
        today = datetime.now().date()
        
        for deadline in deadlines:
            deadline_date = datetime.fromisoformat(deadline['deadline_date']).date()
            days_left = (deadline_date - today).days
            
            if 0 <= days_left <= days:
                upcoming.append({
                    "title": deadline['title'],
                    "deadline_date": deadline['deadline_date'],
                    "days_left": days_left,
                    "category": deadline['category'],
                    "priority": deadline['priority']
                })
        
        return sorted(upcoming, key=lambda x: x['days_left'])
    
    def query_github_consistency(self, days=7):
        """Get GitHub consistency metrics."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        activity = self.db.get_github_activity(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        total_commits = sum([a['commits'] for a in activity])
        active_days = len([a for a in activity if a['commits'] > 0])
        
        return {
            "period": f"{start_date} to {end_date}",
            "total_commits": total_commits,
            "active_days": active_days,
            "consistency_rate": (active_days / days) * 100
        }
