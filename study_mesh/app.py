import streamlit as st
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from src.agents.orchestrator import create_orchestrator_agent
from src.session_manager import SessionManager
import asyncio
from src.config import APP_TITLE, APP_ICON

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and orchestrator
@st.cache_resource
def init_app():
    db = DatabaseManager()
    session_manager = SessionManager()
    orchestrator = create_orchestrator_agent()
    return db, session_manager, orchestrator

db, session_manager, orchestrator = init_app()

# Modern Custom CSS (Tailwind-inspired)
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        text-align: center;
   }
    
    /* Streak counter */
    .streak-badge {
        display: inline-block;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 2rem;
        font-size: 1.5rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
        margin: 1rem 0;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Task cards */
    .task-card {
        background: white;
        padding: 1rem;
        border-radius: 0.75rem;
        border-left: 4px solid #667eea;
        margin: 0.75rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .task-card-completed {
        background: #f0fdf4;
        border-left-color: #22c55e;
        opacity: 0.7;
    }
    
    /* Urgent task highlighting*/
    .urgent-task {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        padding: 1rem;
        border-left: 4px solid #f44336;
        border-radius: 0.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 8px rgba(244, 67, 54, 0.2);
    }
    
    /* Praise message */
    .praise-message {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #f59e0b;
        font-size: 1.1rem;
        font-weight: 500;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }
    
    /* GitHub toggle button */
    .github-toggle {
        background: linear-gradient(135deg, #24292e 0%, #6366f1 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 0.75rem;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(36, 41, 46, 0.3);
    }
    
    .github-toggle:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        border-color: #764ba2;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1f2937;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title(f"{APP_ICON} AI Planner")
    st.markdown("---")
    
    # Check if user profile exists
    profile = db.get_user_profile()
    
    if profile:
        st.success(f"👋 {profile.get('name', 'User')}!")
        
        # Streak display in sidebar
        total_streak = db.get_streak_count()
        if total_streak > 0:
            st.markdown(f"🔥 **{total_streak} Day Streak!**")
        
        st.info(f"🎯 {profile.get('study_goal', 'Not set')[:50]}...")
    else:
        st.warning("⚠️ Complete onboarding first!")
        if st.button("🎯 Start Onboarding"):
            st.switch_page("pages/0_🎯_Onboarding.py")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    
    # Get today's tasks
    today_tasks = db.get_tasks(task_type="daily", status="pending")
    completed_today = db.get_tasks(task_type="daily", status="completed")
    
    st.metric("Today's Tasks", len(today_tasks))
    st.metric("Completed", len(completed_today))
    
    # Get upcoming deadlines
    deadlines = db.get_deadlines(status="pending")
    st.metric("Active Deadlines", len(deadlines))
    
    st.markdown("---")
    st.caption("Powered by Google ADK + Gemini 🤖")

# Main content
if not profile:
    # Show onboarding prompt
    st.markdown('<div class="main-header">🎯 AI Productivity Planner</div>', unsafe_allow_html=True)
    st.warning("### 👋 Welcome! Let's get you started")
    st.info("Please complete your profile setup in **🎯 Onboarding** to unlock all features.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start Onboarding", use_container_width=True):
            st.switch_page("pages/0_🎯_Onboarding.py")
    
    with st.expander("✨ What this planner can do"):
        st.markdown("""
        - 📋 **AI-Powered Task Management** - Personalized daily, weekly, and long-term tasks
        - 📅 **Smart Deadline Tracking** - AI extracts deadlines from URLs
        - 📊 **Progress Analytics** - Visualize your learning journey
        - 💻 **GitHub Streak Tracking** - Build consistent coding habits
        - 📚 **Research Paper Feed** - AI-curated papers based on your interests
        - 🎯 **Multi-Agent AI System** - Orchestrator coordinates specialist agents
        - 🎉 **AI Praise & Motivation** - Get encouragement on task completion
        """)
else:
    # Dashboard for onboarded users
    st.markdown('<div class="main-header">🎯 Your AI Productivity Dashboard</div>', unsafe_allow_html=True)
    
    # Streak counter at top
    total_streak = db.get_streak_count()
    github_streak = db.get_streak_count('github')
    
    col_streak1, col_streak2 = st.columns(2)
    with col_streak1:
        st.markdown(f'<div class="streak-badge">🔥 {total_streak} Day Streak!</div>', unsafe_allow_html=True)
    with col_streak2:
        st.markdown(f'<div class="streak-badge">💻 {github_streak} GitHub Days</div>', unsafe_allow_html=True)
    
    # GitHub Manual Toggle
    st.markdown('<div class="section-header">💻 Daily Coding Check-In</div>', unsafe_allow_html=True)
    
    col_gh1, col_gh2 = st.columns([3, 1])
    with col_gh1:
        if st.button("🚀 Did you push code today?", use_container_width=True, key="github_toggle"):
            # Update streak
            today = datetime.now().date().isoformat()
            db.update_streak(today, 'github')
            
            # Get new streak count
            new_github_streak = db.get_streak_count('github')
            
            # Generate praise using orchestrator
            try:
                praise_prompt = f"Generate a short (1 sentence), enthusiastic congratulations message for maintaining a {new_github_streak}-day GitHub coding streak. Be energetic and encouraging!"
                praise_msg = session_manager.run_agent_sync(orchestrator, "user_default", praise_prompt)
                
                # Save praise
                db.save_praise_message(praise_msg, context="github_streak")
                
                # Display congrats
                st.success(f"🎉 {praise_msg}")
                st.balloons()
                st.rerun()
            except:
                st.success(f"🎉 Awesome! {new_github_streak} day GitHub streak!")
    
    # Latest AI Praise
    latest_praise = db.get_latest_praise()
    if latest_praise:
        st.markdown('<div class="section-header">✨ Latest Encouragement</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="praise-message">💬 {latest_praise["message"]}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Three-column dashboard
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="section-header">📋 Today\'s Focus</div>', unsafe_allow_html=True)
        
        # Daily tasks with checkboxes
        daily_tasks = db.get_tasks(task_type="daily")
        
        if daily_tasks:
            for task in daily_tasks[:5]:
                is_completed = task['status'] == 'completed'
                card_class = "task-card-completed" if is_completed else "task-card"
                
                with st.container():
                    col_check, col_text = st.columns([1, 9])
                    
                    with col_check:
                        checked = st.checkbox("", value=is_completed, key=f"task_{task['id']}")
                        
                        if checked and not is_completed:
                            # Mark as completed
                            db.update_task_status(task['id'], 'completed')
                            
                            # Generate AI praise
                            try:
                                praise_prompt = "Generate a short (10 words or less), energetic praise message for completing a task. Be enthusiastic!"
                                praise_msg = session_manager.run_agent_sync(orchestrator, "user_default", praise_prompt)
                                db.save_praise_message(praise_msg, task['id'], "task_completion")
                                st.success(f"🎉 {praise_msg}")
                            except:
                                st.success("🎉 Great job!")
                            
                            st.rerun()
                    
                    with col_text:
                        st.markdown(f"**{task['title']}**")
                        if task.get('estimated_hours'):
                            st.caption(f"⏱️ {task['estimated_hours']} hours")
        else:
            st.success("✅ All daily tasks completed!")
            st.button("➕ Add New Tasks")
    
    with col2:
        st.markdown('<div class="section-header">📅 Upcoming Deadlines</div>', unsafe_allow_html=True)
        
        deadlines = db.get_deadlines(status="pending")
        
        if deadlines:
            for deadline in deadlines[:4]:
                try:
                    deadline_date = datetime.fromisoformat(deadline['deadline_date'])
                    days_left = (deadline_date - datetime.now()).days
                    
                    if days_left <= 7:
                        st.markdown(f'<div class="urgent-task">🔥 **{deadline["title"]}**<br>{days_left} days left!</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="task-card">📌 **{deadline["title"]}**<br>{days_left} days left</div>', unsafe_allow_html=True)
                except:
                    st.markdown(f'<div class="task-card">📌 **{deadline["title"]}**</div>', unsafe_allow_html=True)
        else:
            st.info("No active deadlines")
    
    with col3:
        st.markdown('<div class="section-header">📊 This Week</div>', unsafe_allow_html=True)
        
        # Get weekly progress
        week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        progress = db.get_progress(start_date=week_start.isoformat())
        
        total_hours = sum([p['study_hours'] for p in progress if p.get('study_hours')])
        st.metric("Study Hours", f"{total_hours:.1f}h")
        
        # Tasks completed this week
        completed_tasks = db.get_tasks(status="completed")
        week_completed = [t for t in completed_tasks if t.get('completed_at', '').startswith(week_start.isoformat()[:7])]
        st.metric("Tasks Completed", len(week_completed))
        
        # Papers read this week
        papers = db.get_papers(is_read=1)
        st.metric("Papers Read", len(papers))
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
    col_x, col_y, col_z = st.columns(3)
    
    with col_x:
        if st.button("➕ Add Task", use_container_width=True):
            st.switch_page("pages/1_📋_Daily_Tasks.py")
    
    with col_y:
        if st.button("📅 Add Deadline", use_container_width=True):
            st.switch_page("pages/2_📅_Deadlines.py")
    
    with col_z:
        if st.button("📚 Find Papers", use_container_width=True):
            st.switch_page("pages/5_📚_Papers.py")

# Footer
st.markdown("---")
st.caption("🎯 AI Productivity Planner - Powered by Multi-Agent AI System | ADK + Gemini 2.5 Flash")
