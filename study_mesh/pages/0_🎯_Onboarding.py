import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from src.agents.orchestrator import create_orchestrator_agent
from src.session_manager import SessionManager
import asyncio
from src.config import APP_TITLE, APP_ICON

# Page configuration
st.set_page_config(
    page_title=f"{APP_TITLE} - Onboarding",
    page_icon=APP_ICON,
    layout="wide"
)

# Initialize database
@st.cache_resource
def init_db():
    return DatabaseManager()

db = init_db()

# Custom CSS
st.markdown("""
<style>
    .onboarding-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="onboarding-header">🎯 Welcome to AI Productivity Planner!</div>', unsafe_allow_html=True)

# Check if already onboarded
profile = db.get_user_profile()

if profile:
    st.success("✅ You've already completed onboarding!")
    st.info(f"**Name:** {profile['name']}")
    st.info(f"**Goal:** {profile['study_goal']}")
    
    if st.button("🔄 Reset and Start Over"):
        # In a real app, you'd clear the profile here
        st.warning("Feature coming soon: profile reset")
    
    if st.button("🏠 Go to Dashboard"):
        st.switch_page("app.py")
else:
    st.markdown("### Let's personalize your learning journey!")
    
    with st.form("onboarding_form"):
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        
        st.markdown("#### 📝 Tell us about yourself")
        name = st.text_input("Your Name", placeholder="e.g., Alex")
        
        st.markdown("#### 🎯What's your main learning goal?")
        study_goal = st.text_area(
            "Study Goal",
            placeholder="e.g., Master Machine Learning and get a job in AI",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ⏰ How many hours can you study daily?")
            hours_per_day = st.slider("Hours per Day", 1, 12, 4)
        
        with col2:
            st.markdown("#### 📅 How many days per week?")
            days_per_week = st.slider("Days per Week", 1, 7, 5)
        
        st.markdown("#### 🔬 What topics interest you?")
        topics = st.text_area(
            "Topics (comma-separated)",
            placeholder="e.g., Machine Learning, NLP, Computer Vision, Transformers",
            height=80
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        submit = st.form_submit_button("✨ Generate My Personalized Plan")
    
    if submit:
        if not name or not study_goal or not topics:
            st.error("⚠️ Please fill in all fields!")
        else:
            with st.spinner("🤖 AI is creating your personalized roadmap..."):
                try:
                    # Save profile
                    db.save_user_profile(name, study_goal, hours_per_day, days_per_week, topics)
                    
                    # Create orchestrator and generate roadmap via Task Planner agent
                    orchestrator = create_orchestrator_agent()
                    session_manager = SessionManager()
                    
                    # Generate initial tasks
                    prompt = f"""Generate a personalized learning roadmap for:
                    Goal: {study_goal}
                    Available time: {hours_per_day} hours/day, {days_per_week} days/week
                    Topics: {topics}
                    
                    Create specific, actionable tasks categorized as:
                    - Daily tasks (things to do every study day)
                    - Weekly tasks (larger goals for the week)
                    - Long-term milestones (major achievements)
                    
                    Make tasks realistic and achievable given the time available.
                    """
                    
                    # Call task planner via orchestrator
                    roadmap = session_manager.run_agent_sync(orchestrator, "user_default", prompt)
                    
                    # Parse and save some initial tasks (simplified for now)
                    # In practice, you'd parse the LLM response to extract structured tasks
                    db.add_task(
                        title="Review AI fundamentals",
                        description="Go through basic concepts",
                        task_type="daily",
                        priority=5,
                        estimated_hours=2
                    )
                    db.add_task(
                        title="Complete one ML tutorial",
                        description="Follow a hands-on tutorial",
                        task_type="weekly",
                        priority=4,
                        estimated_hours=hours_per_day * 2
                    )
                    
                    st.success("🎉 Your personalized plan is ready!")
                    st.markdown("### 📋 Your AI-Generated Roadmap")
                    st.write(roadmap)
                    
                    # Initialize streak
                    from datetime import datetime
                    db.update_streak(datetime.now().date().isoformat(), 'general')
                    
                    st.balloons()
                    
                    if st.button("🚀 Go to Dashboard"):
                        st.switch_page("app.py")
                        
                except Exception as e:
                    st.error(f"❌ Error generating roadmap: {str(e)}")
                    st.info("💡 Try again or contact support if the issue persists.")
