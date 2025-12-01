import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "planner.db")

class DatabaseManager:
    """Manages all database operations for the planner."""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema if it doesn't exist."""
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        
        with sqlite3.connect(self.db_path) as conn:
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())
            conn.commit()
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # User Profile
    def get_user_profile(self):
        """Get user profile."""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def save_user_profile(self, name, study_goal, hours_per_day, days_per_week, topics):
        """Save or update user profile."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO user_profile (name, study_goal, hours_per_day, days_per_week, topics)
                VALUES (?, ?, ?, ?, ?)
            """, (name, study_goal, hours_per_day, days_per_week, topics))
            conn.commit()
    
    # Tasks
    def add_task(self, title, description, task_type, priority=0, estimated_hours=None, due_date=None):
        """Add a new task."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO tasks (title, description, task_type, priority, estimated_hours, due_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, description, task_type, priority, estimated_hours, due_date))
            conn.commit()
            return cursor.lastrowid
    
    def get_tasks(self, task_type=None, status=None):
        """Get tasks filtered by type and/or status."""
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        if task_type:
            query += " AND task_type = ?"
            params.append(task_type)
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY priority DESC, due_date ASC"
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_task_status(self, task_id, status):
        """Update task status."""
        completed_at = datetime.now().isoformat() if status == 'completed' else None
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE tasks SET status = ?, completed_at = ?
                WHERE id = ?
            """, (status, completed_at, task_id))
            conn.commit()
    
    def delete_task(self, task_id):
        """Delete a task."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?",(task_id,))
            conn.commit()
    
    # Deadlines
    def add_deadline(self, title, description, deadline_date, category, priority=0, requirements=None):
        """Add a new deadline."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO deadlines (title, description, deadline_date, category, priority, requirements)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, description, deadline_date, category, priority, requirements))
            conn.commit()
            return cursor.lastrowid
    
    def get_deadlines(self, status=None):
        """Get deadlines."""
        query = "SELECT * FROM deadlines WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY deadline_date ASC"
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_deadline_status(self, deadline_id, status, completed_requirements=None):
        """Update deadline status."""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE deadlines SET status = ?, completed_requirements = ?
                WHERE id = ?
            """, (status, completed_requirements, deadline_id))
            conn.commit()
    
    # Progress History
    def add_progress(self, task_id, study_hours, notes, date):
        """Add progress entry."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO progress_history (task_id, study_hours, notes, date)
                VALUES (?, ?, ?, ?)
            """, (task_id, study_hours, notes, date))
            conn.commit()
    
    def get_progress(self, start_date=None, end_date=None):
        """Get progress history."""
        query = "SELECT * FROM progress_history WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date DESC"
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # GitHub Activity
    def save_github_activity(self, date, commits, repositories, activity_summary):
        """Save GitHub activity for a date."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO github_activity (date, commits, repositories, activity_summary)
                VALUES (?, ?, ?, ?)
            """, (date, commits, repositories, activity_summary))
            conn.commit()
    
    def get_github_activity(self, start_date=None, end_date=None):
        """Get GitHub activity."""
        query = "SELECT * FROM github_activity WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date DESC"
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # Papers
    def save_paper(self, title, authors, abstract, arxiv_id, pdf_url, published_date, summary=None):
        """Save a research paper."""
        with self.get_connection() as conn:
            try:
                conn.execute("""
                    INSERT INTO papers (title, authors, abstract, arxiv_id, pdf_url, published_date, summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (title, authors, abstract, arxiv_id, pdf_url, published_date, summary))
                conn.commit()
            except sqlite3.IntegrityError:
                pass  # Paper already exists
    
    def get_papers(self, is_read=None, limit=None):
        """Get papers."""
        query = "SELECT * FROM papers WHERE 1=1"
        params = []
        
        if is_read is not None:
            query += " AND is_read = ?"
            params.append(is_read)
        
        query += " ORDER BY published_date DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_paper_read(self, paper_id):
        """Mark paper as read."""
        with self.get_connection() as conn:
            conn.execute("UPDATE papers SET is_read = 1 WHERE id = ?", (paper_id,))
            conn.commit()
    
    # Social Posts
    def save_post(self, platform, content, achievement):
        """Save a social media post draft."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO social_posts (platform, content, achievement)
                VALUES (?, ?, ?)
            """, (platform, content, achievement))
            conn.commit()
            return cursor.lastrowid
    
    def get_posts(self, is_posted=None):
        """Get social media posts."""
        query = "SELECT * FROM social_posts WHERE 1=1"
        params = []
        
        if is_posted is not None:
            query += " AND is_posted = ?"
            params.append(is_posted)
        
        query += " ORDER BY created_at DESC"
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # Reminders
    def add_reminder(self, reminder_type, message, target_date=None):
        """Add a reminder."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO reminders (reminder_type, message, target_date)
                VALUES (?, ?, ?)
            """, (reminder_type, message, target_date))
            conn.commit()
    
    def get_active_reminders(self):
        """Get active reminders."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM reminders 
                WHERE is_active = 1 AND is_dismissed = 0
                ORDER BY target_date ASC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def dismiss_reminder(self, reminder_id):
        """Dismiss a reminder."""
        with self.get_connection() as conn:
            conn.execute("UPDATE reminders SET is_dismissed = 1 WHERE id = ?", (reminder_id,))
            conn.commit()
    
    # User Streaks (NEW)
    def update_streak(self, date=None, activity_type='general'):
        """Update daily streak tracking."""
        if date is None:
            date = datetime.now().date().isoformat()
        
        with self.get_connection() as conn:
            try:
                conn.execute("""
                    INSERT INTO user_streaks (date, activity_type)
                    VALUES (?, ?)
                """, (date, activity_type))
                conn.commit()
            except sqlite3.IntegrityError:
                # Date already exists, update activity type if different
                conn.execute("""
                    UPDATE user_streaks SET activity_type = ?
                    WHERE date = ?
                """, (activity_type, date))
                conn.commit()
    
    def get_streak_count(self, activity_type=None):
        """Calculate current consecutive streak."""
        with self.get_connection() as conn:
            query = "SELECT date FROM user_streaks"
            params = []
            
            if activity_type:
                query += " WHERE activity_type = ?"
                params.append(activity_type)
            
            query += " ORDER BY date DESC"
            
            cursor = conn.execute(query, params)
            dates = [row['date'] for row in cursor.fetchall()]
            
            if not dates:
                return 0
            
            # Calculate streak
            streak = 1
            current_date = datetime.fromisoformat(dates[0]).date()
            
            for date_str in dates[1:]:
                date = datetime.fromisoformat(date_str).date()
                if (current_date - date).days == 1:
                    streak += 1
                    current_date = date
                else:
                    break
            
            return streak
    
    def get_streaks_history(self, days=30):
        """Get streak history for the last N days."""
        with self.get_connection() as conn:
            start_date = (datetime.now().date() - timedelta(days=days)).isoformat()
            cursor = conn.execute("""
                SELECT * FROM user_streaks
                WHERE date >= ?
                ORDER BY date DESC
            """, (start_date,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Praise Messages (NEW)
    def save_praise_message(self, message, task_id=None, context=None):
        """Store AI-generated praise."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO praise_messages (message, task_id, context)
                VALUES (?, ?, ?)
            """, (message, task_id, context))
            conn.commit()
            return cursor.lastrowid
    
    def get_latest_praise(self, limit=1):
        """Get most recent praise message(s)."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM praise_messages
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            results = [dict(row) for row in cursor.fetchall()]
            return results[0] if limit == 1 and results else results
    
    def get_praise_history(self, days=7):
        """Get recent praise messages."""
        with self.get_connection() as conn:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            cursor = conn.execute("""
                SELECT * FROM praise_messages
                WHERE created_at >= ?
                ORDER BY created_at DESC
            """, (start_date,))
            return [dict(row) for row in cursor.fetchall()]
