import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from database.db_manager import DatabaseManager
from src.agents.orchestrator import create_orchestrator_agent
from src.session_manager import SessionManager

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

@st.cache_resource
def init_resources():
    return DatabaseManager(), SessionManager(), create_orchestrator_agent()

db, session_manager, orchestrator = init_resources()

st.title("⚙️ Settings & Profile")

# Tabs
tab1, tab2 = st.tabs(["User Profile", "API Configuration"])

with tab1:
    st.markdown("### 👤 Your Profile")
    
    profile = db.get_user_profile()
    
    with st.form("profile_form"):
        st.markdown("#### Tell us about your goals")
        
        name = st.text_input("Name", value=profile['name'] if profile else "")
        study_goal = st.text_area(
            "What do you want to study or achieve?",
            value=profile['study_goal'] if profile else "",
            placeholder="e.g., Master deep learning, Get into AI research, Build ML projects"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            hours_per_day = st.number_input(
                "Hours per day you can study",
                min_value=0.5,
                max_value=12.0,
                step=0.5,
                value=float(profile['hours_per_day']) if profile else 2.0
            )
        with col2:
            days_per_week = st.slider(
                "Days per week available",
                min_value=1,
                max_value=7,
                value=int(profile['days_per_week']) if profile else 5
            )
        
        topics = st.text_area(
            "Topics or tasks for your roadmap",
            value=profile['topics'] if profile else "",
            placeholder="e.g., PyTorch, Research papers, Build projects, Apply for scholarships"
        )
        
        if st.form_submit_button("💾 Save Profile", use_container_width=True):
            if name and study_goal:
                db.save_user_profile(name, study_goal, hours_per_day, days_per_week, topics)
                st.success("✅ Profile saved successfully!")
                
                # Generate roadmap
                with st.spinner("🤖 Generating your personalized roadmap..."):
                    prompt = f"""Create a detailed study roadmap for:
                    Goal: {study_goal}
                    Available: {hours_per_day} hours/day, {days_per_week} days/week
                    Topics: {topics}
                    
                    Break it down into weeks and specific tasks."""
                    
                    roadmap = session_manager.run_agent_sync(orchestrator, "user_default", prompt)
                    st.markdown("### 🗺️ Your Personalized Roadmap")
                    st.markdown(roadmap)
                
                st.rerun()
            else:
                st.error("Please fill in at least Name and Study Goal")
    
    if profile:
        st.markdown("---")
        st.markdown("### 📊 Current Profile")
        st.info(f"""
        **Name:** {profile['name']}  
        **Goal:** {profile['study_goal']}  
        **Study Time:** {profile['hours_per_day']} hours/day, {profile['days_per_week']} days/week  
        **Topics:** {profile['topics']}
        """)

with tab2:
    st.markdown("### 🔑 API Configuration")
    
    st.info("""
    Configure your API keys to enable all features:
    - **Google API Key**: Required for AI features (roadmap generation, summaries, posts)
    - **GitHub Token**: Optional, for GitHub activity tracking
    """)
    
    st.markdown("#### Current Configuration")
    
    from src.config import GOOGLE_API_KEY, GITHUB_TOKEN
    
    col1, col2 = st.columns(2)
    with col1:
        if GOOGLE_API_KEY and GOOGLE_API_KEY != "your_api_key_here":
            st.success("✅ Google API Key configured")
        else:
            st.error("❌ Google API Key not configured")
    
    with col2:
        if GITHUB_TOKEN and GITHUB_TOKEN != "your_github_token_here":
            st.success("✅ GitHub Token configured")
        else:
            st.warning("⚠️ GitHub Token not configured")
    
    st.markdown("---")
    st.markdown("#### How to Configure")
    
    with st.expander("🔧 Setup Instructions"):
        st.markdown("""
        1. **Google API Key** (Required):
           - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
           - Create a new API key
           - Copy the key
           - Open `.env` file in the planner folder
           - Replace `your_api_key_here` with your actual key
        
        2. **GitHub Token** (Optional):
           - Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
           - Generate new token (classic)
           - Select scopes: `repo`, `read:user`
           - Copy the token
           - Add to `.env` file: `GITHUB_TOKEN=your_token_here`
        
        3. **Restart the app** after updating `.env`
        """)
    
    st.markdown("---")
    st.markdown("### 🗑️ Data Management")
    
    if st.button("🔄 Reset All Data", type="secondary"):
        if st.checkbox("I understand this will delete all my data"):
            # This would require implementing a reset function
            st.warning("Data reset functionality - to be implemented")
