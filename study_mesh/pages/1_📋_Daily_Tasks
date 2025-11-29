import streamlit as st
import sys
import os
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from src.agents.orchestrator import create_orchestrator_agent
from src.session_manager import SessionManager
from src.config import TASK_TYPES, TASK_STATUS

st.set_page_config(page_title="Daily Tasks", page_icon="📋", layout="wide")

@st.cache_resource
def init_resources():
    return DatabaseManager(), SessionManager(), create_orchestrator_agent()

db, session_manager, orchestrator = init_resources()

st.title("📋 Daily Task Manager")

# Tabs
tab1, tab2, tab3 = st.tabs(["Today's Tasks", "Weekly Tasks", "Long-term Goals"])

with tab1:
    st.markdown("### Today's Tasks")
    
    # Add new task
    with st.expander("➕ Add New Daily Task"):
        with st.form("add_daily_task"):
            title = st.text_input("Task Title*")
            description = st.text_area("Description")
            col1, col2 = st.columns(2)
            with col1:
                estimated_hours = st.number_input("Estimated Hours", min_value=0.5, max_value=8.0, step=0.5)
            with col2:
                priority = st.slider("Priority", 1, 5, 3)
            
            if st.form_submit_button("Add Task"):
                if title:
                    db.add_task(
                        title=title,
                        description=description,
                        task_type="daily",
                        priority=priority,
                        estimated_hours=estimated_hours,
                        due_date=date.today().isoformat()
                    )
                    st.success(f"✅ Task '{title}' added!")
                    st.rerun()
                else:
                    st.error("Please enter a task title")
    
    # Display daily tasks
    daily_tasks = db.get_tasks(task_type="daily")
    
    if daily_tasks:
        # Separate by status
        pending = [t for t in daily_tasks if t['status'] == 'pending']
        completed = [t for t in daily_tasks if t['status'] == 'completed']
        
        # Pending tasks
        if pending:
            st.markdown("#### 🔄 Pending")
            for task in pending:
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    st.markdown(f"**{task['title']}**")
                    if task['description']:
                        st.caption(task['description'])
                    if task['estimated_hours']:
                        st.caption(f"⏱️ {task['estimated_hours']}h | Priority: {'⭐' * task['priority']}")
                with col_b:
                    if st.button("✅ Complete", key=f"complete_{task['id']}"):
                        db.update_task_status(task['id'], 'completed')
                        # Add to progress
                        db.add_progress(
                            task_id=task['id'],
                            study_hours=task['estimated_hours'] or 0,
                            notes=f"Completed: {task['title']}",
                            date=date.today().isoformat()
                        )
                        st.success("Task completed!")
                        st.rerun()
                with col_c:
                    if st.button("🗑️", key=f"delete_{task['id']}"):
                        db.delete_task(task['id'])
                        st.rerun()
                st.markdown("---")
        
        # Completed tasks
        if completed:
            with st.expander(f"✅ Completed ({len(completed)})"):
                for task in completed:
                    st.markdown(f"~~{task['title']}~~")
                    if task['completed_at']:
                        st.caption(f"Completed: {task['completed_at'][:10]}")
    else:
        st.info("No daily tasks yet. Add one above!")
    
    # AI suggestion
    if st.button("🤖 Generate AI Task Suggestions"):
        profile = db.get_user_profile()
        if profile:
            with st.spinner("Generating personalized tasks..."):
                prompt = f"""Based on this user profile, suggest 3-5 specific daily tasks for today:
                
Study Goal: {profile['study_goal']}
Daily Hours Available: {profile['hours_per_day']}

Create practical, actionable tasks that can be completed today."""
                
                suggestions = session_manager.run_agent_sync(orchestrator, "user_default", prompt)
                st.markdown("### 💡 AI Suggestions")
                st.markdown(suggestions)
        else:
            st.warning("Please complete your profile in Settings first")

with tab2:
    st.markdown("### Weekly Goals")
    
    # Add weekly task
    with st.expander("➕ Add Weekly Goal"):
        with st.form("add_weekly_task"):
            title = st.text_input("Goal Title*")
            description = st.text_area("Description")
            col1, col2 = st.columns(2)
            with col1:
                estimated_hours = st.number_input("Estimated Hours", min_value=1.0, max_value=40.0, step=1.0)
            with col2:
                priority = st.slider("Priority", 1, 5, 3)
            
            if st.form_submit_button("Add Goal"):
                if title:
                    db.add_task(
                        title=title,
                        description=description,
                        task_type="weekly",
                        priority=priority,
                        estimated_hours=estimated_hours
                    )
                    st.success(f"✅ Weekly goal '{title}' added!")
                    st.rerun()
    
    # Display weekly tasks
    weekly_tasks = db.get_tasks(task_type="weekly")
    
    if weekly_tasks:
        for task in weekly_tasks:
            status_emoji = "✅" if task['status'] == 'completed' else "🔄"
            st.markdown(f"{status_emoji} **{task['title']}**")
            if task['description']:
                st.caption(task['description'])
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if task['status'] != 'completed':
                    if st.button("Mark Complete", key=f"weekly_complete_{task['id']}"):
                        db.update_task_status(task['id'], 'completed')
                        st.rerun()
            with col2:
                if st.button("Delete", key=f"weekly_delete_{task['id']}"):
                    db.delete_task(task['id'])
                    st.rerun()
            st.markdown("---")
    else:
        st.info("No weekly goals yet")

with tab3:
    st.markdown("### Long-term Objectives")
    
    # Add long-term task
    with st.expander("➕ Add Long-term Objective"):
        with st.form("add_longterm_task"):
            title = st.text_input("Objective Title*")
            description = st.text_area("Description")
            priority = st.slider("Priority", 1, 5, 3)
            
            if st.form_submit_button("Add Objective"):
                if title:
                    db.add_task(
                        title=title,
                        description=description,
                        task_type="long-term",
                        priority=priority
                    )
                    st.success(f"✅ Objective '{title}' added!")
                    st.rerun()
    
    # Display long-term tasks
    longterm_tasks = db.get_tasks(task_type="long-term")
    
    if longterm_tasks:
        for task in longterm_tasks:
            status_emoji = "✅" if task['status'] == 'completed' else "🎯"
            st.markdown(f"{status_emoji} **{task['title']}**")
            if task['description']:
                st.caption(task['description'])
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if task['status'] != 'completed':
                    if st.button("Mark Complete", key=f"longterm_complete_{task['id']}"):
                        db.update_task_status(task['id'], 'completed')
                        st.rerun()
            with col2:
                if st.button("Delete", key=f"longterm_delete_{task['id']}"):
                    db.delete_task(task['id'])
                    st.rerun()
            st.markdown("---")
    else:
        st.info("No long-term objectives yet")
