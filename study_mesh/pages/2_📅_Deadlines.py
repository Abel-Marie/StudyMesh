import streamlit as st
import sys
import os
from datetime import datetime, date
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from src.agents.orchestrator import create_orchestrator_agent
from src.session_manager import SessionManager
import asyncio
from src.config import DEADLINE_CATEGORIES

st.set_page_config(page_title="Deadlines", page_icon="📅", layout="wide")

@st.cache_resource
def init_resources():
    return DatabaseManager(), SessionManager(), create_orchestrator_agent()

db, session_manager, orchestrator = init_resources()

# Modern CSS
st.markdown("""
<style>
    .deadline-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .ai-parser-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid #38bdf8;
        margin: 1rem 0;
    }
    .deadline-urgent {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 5px solid #ef4444;
        margin: 1rem 0;
    }
    .deadline-soon {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 5px solid #f59e0b;
        margin: 1rem 0;
    }
    .deadline-normal {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 5px solid #22c55e;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="deadline-header">📅 Smart Deadline Tracker</div>', unsafe_allow_html=True)

# AI-Powered URL/Text Parser
st.markdown("---")
st.markdown("### 🤖 AI Deadline Extractor")
st.markdown('<div class="ai-parser-box">', unsafe_allow_html=True)

st.write("Paste an opportunity URL or description, and AI will automatically extract the deadline and requirements!")

url_or_text = st.text_area(
    "Paste URL or Text",
    placeholder="Example:\nGoogle Summer of Code 2025 applications due March 15, 2025\n\nRequirements:\n- Resume\n- Project Proposal\n- GitHub Profile\n- 2 References",
    height=150
)

if st.button("✨ Extract with AI", type="primary"):
    if url_or_text.strip():
        with st.spinner("🤖 AI is analyzing the content..."):
            try:
                # Use deadline_parser agent via orchestrator
                parse_prompt = f"""Extract deadline information from this text or URL:

{url_or_text}

Return a JSON object with:
- title: The opportunity/deadline name
- deadline_date: In YYYY-MM-DD format
- description: Brief description
- requirements: Array of requirement strings
- category: One of: scholarship, internship, competition, application, other
- priority: Number 1-5 based on importance

If any field cannot be determined, use reasonable defaults or "Not specified".
"""
                
                response_output = session_manager.run_agent_sync(orchestrator, "user_default", parse_prompt)
                result_text = response_output
                
                # Try to parse JSON from response
                try:
                    # Extract JSON from markdown code blocks if present
                    if "```json" in result_text:
                        json_start = result_text.find("```json") + 7
                        json_end = result_text.find("```", json_start)
                        json_str = result_text[json_start:json_end].strip()
                    elif "```" in result_text:
                        json_start = result_text.find("```") + 3
                        json_end = result_text.find("```", json_start)
                        json_str = result_text[json_start:json_end].strip()
                    else:
                        # Try to find JSON object directly
                        json_start = result_text.find("{")
                        json_end = result_text.rfind("}") + 1
                        json_str = result_text[json_start:json_end]
                    
                    parsed_data = json.loads(json_str)
                    
                    st.success("✅ AI successfully extracted deadline information!")
                    
                    # Display extracted data
                    st.markdown("#### Extracted Information:")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Title:** {parsed_data.get('title', 'N/A')}")
                        st.write(f"**Deadline:** {parsed_data.get('deadline_date', 'N/A')}")
                        st.write(f"**Category:** {parsed_data.get('category', 'N/A')}")
                        st.write(f"**Priority:** {'⭐' * parsed_data.get('priority', 3)}")
                    
                    with col2:
                        st.write(f"**Description:** {parsed_data.get('description', 'N/A')}")
                        st.write("**Requirements:**")
                        requirements = parsed_data.get('requirements', [])
                        for req in requirements:
                            st.write(f"• {req}")
                    
                    # Save button
                    if st.button("💾 Save to Deadlines"):
                        db.add_deadline(
                            title=parsed_data.get('title', 'Unknown'),
                            description=parsed_data.get('description', ''),
                            deadline_date=parsed_data.get('deadline_date', date.today().isoformat()),
                            category=parsed_data.get('category', 'other'),
                            priority=parsed_data.get('priority', 3),
                            requirements='\n'.join(parsed_data.get('requirements', []))
                        )
                        st.success(f"✅ Saved: {parsed_data.get('title')}")
                        st.rerun()
                
                except json.JSONDecodeError:
                    st.warning("⚠️ Could not parse structured data. Here's the AI response:")
                    st.write(result_text)
                    st.info("💡 You can manually add the deadline using the form below.")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Try the manual form below instead.")
    else:
        st.warning("Please paste some text or URL first!")

st.markdown('</div>', unsafe_allow_html=True)

# Manual deadline addition
st.markdown("---")
with st.expander("➕ Add Deadline Manually"):
    with st.form("add_deadline"):
        title = st.text_input("Title* (e.g., Mila Fellowship Application)")
        description = st.text_area("Description")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            deadline_date = st.date_input("Deadline Date*", min_value=date.today())
        with col2:
            category = st.selectbox("Category", DEADLINE_CATEGORIES)
        with col3:
            priority = st.slider("Priority", 1, 5, 3)
        
        requirements = st.text_area(
            "Requirements (one per line)",
            placeholder="CV\nStatement of Purpose\nRecommendation Letters\nTranscripts"
        )
        
        if st.form_submit_button("Add Deadline"):
            if title and deadline_date:
                db.add_deadline(
                    title=title,
                    description=description,
                    deadline_date=deadline_date.isoformat(),
                    category=category,
                    priority=priority,
                    requirements=requirements
                )
                st.success(f"✅ Deadline '{title}' added!")
                st.rerun()
            else:
                st.error("Please fill in required fields")

# Display deadlines
st.markdown("---")
st.markdown("### 📋 Active Deadlines")

deadlines = db.get_deadlines(status="pending")

if deadlines:
    # Sort by deadline date
    deadlines.sort(key=lambda x: x['deadline_date'])
    
    for deadline in deadlines:
        try:
            days_left = (datetime.fromisoformat(deadline['deadline_date']) - datetime.now()).days
            
            # Color code by urgency
            if days_left <= 3:
                urgency_color = "🔴"
                urgency_text = "URGENT"
                card_class = "deadline-urgent"
            elif days_left <= 7:
                urgency_color = "🟡"
                urgency_text = "Soon"
                card_class = "deadline-soon"
            else:
                urgency_color = "🟢"
                urgency_text = "Upcoming"
                card_class = "deadline-normal"
            
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"### {urgency_color} {deadline['title']}")
                st.caption(f"{urgency_text} - **{days_left} days left** | {deadline['category']}")
                
                if deadline.get('description'):
                    st.markdown(deadline['description'])
                
                # Requirements checklist
                if deadline.get('requirements'):
                    st.markdown("**Requirements:**")
                    requirements_list = deadline['requirements'].split('\n')
                    completed_reqs = deadline.get('completed_requirements', '').split('\n') if deadline.get('completed_requirements') else []
                    
                    for req in requirements_list:
                        if req.strip():
                            is_done = req.strip() in completed_reqs
                            checkbox_key = f"req_{deadline['id']}_{req[:20]}"
                            
                            if st.checkbox(req.strip(), value=is_done, key=checkbox_key):
                                if not is_done:
                                    # Add to completed
                                    new_completed = completed_reqs + [req.strip()]
                                    db.update_deadline_status(
                                        deadline['id'],
                                        'in_progress',
                                        '\n'.join(new_completed)
                                    )
                                    st.rerun()
                            else:
                                if is_done:
                                    # Remove from completed
                                    new_completed = [r for r in completed_reqs if r != req.strip()]
                                    db.update_deadline_status(
                                        deadline['id'],
                                        'pending' if not new_completed else 'in_progress',
                                        '\n'.join(new_completed)
                                    )
                                    st.rerun()
            
            with col2:
                st.markdown(f"**📅 {deadline['deadline_date']}**")
                st.caption(f"Priority: {'⭐' * deadline['priority']}")
                
                if st.button("✅ Complete", key=f"complete_{deadline['id']}"):
                    db.update_deadline_status(deadline['id'], 'completed', deadline.get('completed_requirements', ''))
                    st.success("Deadline marked as completed!")
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error displaying deadline: {e}")
else:
    st.info("📭 No active deadlines. Use the AI extractor above or add one manually!")

# Completed deadlines
completed_deadlines = db.get_deadlines(status="completed")
if completed_deadlines:
    with st.expander(f"✅ Completed Deadlines ({len(completed_deadlines)})"):
        for deadline in completed_deadlines:
            st.markdown(f"✓ ~~{deadline['title']}~~ - {deadline['deadline_date']}")
