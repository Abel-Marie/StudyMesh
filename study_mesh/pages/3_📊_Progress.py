import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from src.agents.orchestrator import create_orchestrator_agent
from src.session_manager import SessionManager

st.set_page_config(page_title="Progress", page_icon="📊", layout="wide")

@st.cache_resource
def init_resources():
    return DatabaseManager(), SessionManager(), create_orchestrator_agent()

db, session_manager, orchestrator = init_resources()

st.title("📊 Progress Analytics")

# Date range selector
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("From", value=datetime.now().date() - timedelta(days=30))
with col2:
    end_date = st.date_input("To", value=datetime.now().date())

# Get progress data
progress_data = db.get_progress(start_date=start_date.isoformat(), end_date=end_date.isoformat())
tasks = db.get_tasks()

# Metrics
col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    total_hours = sum([p['study_hours'] for p in progress_data if p['study_hours']])
    st.metric("Total Study Hours", f"{total_hours:.1f}h")

with col_b:
    completed_tasks = [t for t in tasks if t['status'] == 'completed']
    st.metric("Tasks Completed", len(completed_tasks))

with col_c:
    avg_hours = total_hours / max(1, (end_date - start_date).days + 1)
    st.metric("Avg Hours/Day", f"{avg_hours:.1f}h")

with col_d:
    completion_rate = (len(completed_tasks) / max(1, len(tasks))) * 100
    st.metric("Completion Rate", f"{completion_rate:.0f}%")

st.markdown("---")

# Charts
tab1, tab2, tab3 = st.tabs(["Study Hours", "Task Completion", "Weekly Summary"])

with tab1:
    st.markdown("### 📈 Study Hours Over Time")
    
    if progress_data:
        # Aggregate by date
        hours_by_date = {}
        for p in progress_data:
            date = p['date']
            if date not in hours_by_date:
                hours_by_date[date] = 0
            hours_by_date[date] += p['study_hours'] or 0
        
        df = pd.DataFrame([
            {"Date": date, "Hours": hours}
            for date, hours in sorted(hours_by_date.items())
        ])
        
        fig = px.line(df, x="Date", y="Hours", markers=True)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No study hours logged yet")

with tab2:
    st.markdown("### ✅ Task Completion by Type")
    
    if tasks:
        task_stats = {}
        for task_type in ['daily', 'weekly', 'long-term']:
            type_tasks = [t for t in tasks if t['task_type'] == task_type]
            completed = [t for t in type_tasks if t['status'] == 'completed']
            task_stats[task_type] = {
                'Total': len(type_tasks),
                'Completed': len(completed),
                'Pending': len(type_tasks) - len(completed)
            }
        
        df = pd.DataFrame(task_stats).T
        st.bar_chart(df[['Completed', 'Pending']])
    else:
        st.info("No tasks yet")

with tab3:
    st.markdown("### 📅 Weekly Summary")
    
    # Get this week's data
    week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    week_progress = db.get_progress(start_date=week_start.isoformat())
    
    week_hours = sum([p['study_hours'] for p in week_progress if p['study_hours']])
    week_tasks = [t for t in tasks if t['status'] == 'completed' and t['completed_at'] and t['completed_at'].startswith(week_start.isoformat()[:7])]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("This Week's Hours", f"{week_hours:.1f}h")
        st.metric("Tasks Completed", len(week_tasks))
    
    with col2:
        profile = db.get_user_profile()
        if profile:
            target_hours = profile['hours_per_day'] * profile['days_per_week']
            progress_pct = (week_hours / target_hours * 100) if target_hours > 0 else 0
            st.metric("Weekly Goal Progress", f"{progress_pct:.0f}%")
            st.progress(min(progress_pct / 100, 1.0))

st.markdown("---")

# Generate social post
st.markdown("### 📱 Share Your Progress")

if st.button("🤖 Generate Social Media Post"):
    if completed_tasks:
        achievement = f"Completed {len(completed_tasks)} tasks and studied {total_hours:.1f} hours in the past {(end_date - start_date).days + 1} days"
        
        platform = st.selectbox("Platform", ["linkedin", "twitter", "medium"])
        
        with st.spinner("Generating post..."):
            prompt = f"""Create a {platform} post about this achievement:
            "{achievement}"
            
            Make it engaging, professional (if LinkedIn) or catchy (if Twitter).
            Include relevant hashtags."""
            
            post = session_manager.run_agent_sync(orchestrator, "user_default", prompt)
            
            st.markdown("#### Generated Post:")
            st.text_area("", post, height=200)
            
            # Save to database
            db.save_post(platform, post, achievement)
            
            st.success("✅ Post generated! Copy and share on your platform.")
    else:
        st.warning("Complete some tasks first to generate a post!")
