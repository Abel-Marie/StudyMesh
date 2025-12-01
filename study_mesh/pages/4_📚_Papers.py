import streamlit as st
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from src.paper_finder import PaperFinder
from src.agents.orchestrator import create_orchestrator_agent
from src.session_manager import SessionManager
import asyncio

st.set_page_config(page_title="Papers", page_icon="📚", layout="wide")

@st.cache_resource
def init_resources():
    return DatabaseManager(), PaperFinder(), SessionManager(), create_orchestrator_agent()

db, paper_finder, session_manager, orchestrator = init_resources()

# Modern CSS
st.markdown("""
<style>
    .papers-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .paper-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    .paper-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    .paper-card-read {
        background: #f0fdf4;
        border-left-color: #22c55e;
        opacity: 0.8;
    }
    .ai-box {
        background: linear-gradient(135deg, #ddd6fe 0%, #e9d5ff 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        border: 2px solid #a78bfa;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="papers-header">📚 Research Papers Feed</div>', unsafe_allow_html=True)

# Get user profile
profile = db.get_user_profile()

if not profile:
    st.warning("⚠️ Please complete onboarding in Settings to personalize your paper feed!")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["🌟 Daily Feed", "🔍 Search", "📚 My Library"])

with tab1:
    st.markdown("### 🤖 AI-Curated Papers")
    st.markdown('<div class="ai-box">', unsafe_allow_html=True)
    st.write(f"Based on your interests: **{profile.get('topics', 'AI topics')}**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    topic = st.text_input(
        "Customize Topic (optional)",
        value=profile.get('topics', '').split(',')[0] if profile.get('topics') else '',
        placeholder="e.g., Transformers, Reinforcement Learning"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        num_papers = st.slider("Number of papers", 3, 10, 5)
    
    if st.button("📡 Fetch Daily Papers", type="primary"):
        with st.spinner("🤖 AI is curating papers for you..."):
            try:
                # Use Research Agent via orchestrator
                papers = paper_finder.get_daily_papers(topic or profile.get('topics', 'AI'), count=num_papers)
                
                if papers:
                    st.success(f"✅ Found {len(papers)} relevant papers!")
                    
                    for i, paper in enumerate(papers, 1):
                        st.markdown(f'<div class="paper-card">', unsafe_allow_html=True)
                        
                        # Paper header
                        st.markdown(f"### 📄 {paper['title']}")
                        st.caption(f"👥 {paper['authors']} | 📅 {paper['published_date']}")
                        
                        # Abstract
                        with st.expander("📖 Abstract"):
                            st.write(paper['abstract'])
                        
                        # AI Summary generation
                        col_sum1, col_sum2 = st.columns(2)
                        
                        with col_sum1:
                            if st.button("🤖 Generate AI Summary", key=f"summary_{i}"):
                                with st.spinner("AI is reading the paper..."):
                                    try:
                                        summary_prompt = f"""Provide a concise 2-3 sentence summary of this research paper for a student:
                                        
Title: {paper['title']}
Abstract: {paper['abstract'][:500]}

Focus on: What problem it solves, the approach, and key findings."""
                                        
                                        response_output = session_manager.run_agent_sync(orchestrator, "user_default", summary_prompt)
                                        summary = response_output
                                        
                                        st.markdown("**🎯 AI Summary:**")
                                        st.info(summary)
                                        
                                        # Save paper with summary
                                        db.save_paper(
                                            title=paper['title'],
                                            authors=paper['authors'],
                                            abstract=paper['abstract'],
                                            arxiv_id=paper['arxiv_id'],
                                            pdf_url=paper['pdf_url'],
                                            published_date=paper['published_date'],
                                            summary=summary
                                        )
                                        st.success("💾 Saved to library with summary!")
                                    except Exception as e:
                                        import traceback
                                        error_details = traceback.format_exc()
                                        st.error(f"❌ Error generating summary: {str(e)}")
                                        with st.expander("📋 Technical Details"):
                                            st.code(error_details)
                                        st.warning("💡 This might be due to API rate limits. Please try again in a few minutes.")
                        
                        with col_sum2:
                            if st.button("💾 Save to Library", key=f"save_{i}"):
                                db.save_paper(
                                    title=paper['title'],
                                    authors=paper['authors'],
                                    abstract=paper['abstract'],
                                    arxiv_id=paper['arxiv_id'],
                                    pdf_url=paper['pdf_url'],
                                    published_date=paper['published_date']
                                )
                                st.success("✅ Saved!")
                        
                        # PDF link
                        st.link_button("📄 View PDF", paper['pdf_url'], use_container_width=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown("---")
                
                else:
                    st.warning("No papers found. Try a different topic!")
            
            except Exception as e:
                st.error(f"❌ Error fetching papers: {e}")

with tab2:
    st.markdown("### 🔍 Search arXiv")
    
    search_query = st.text_input(
        "Search Query",
        placeholder="e.g., attention mechanisms in transformers"
    )
    
    if st.button("🔎 Search"):
        if search_query:
            with st.spinner("Searching arXiv database..."):
                try:
                    results = paper_finder.search_papers(search_query, max_results=10)
                    
                    if results:
                        st.success(f"📊 Found {len(results)} papers")
                        
                        for paper in results:
                            st.markdown(f'<div class="paper-card">', unsafe_allow_html=True)
                            st.markdown(f"**{paper['title']}**")
                            st.caption(f"{paper['authors']} | {paper['published_date']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.link_button("📄 View PDF", paper['pdf_url'], key=f"search_{paper['arxiv_id']}")
                            with col2:
                                if st.button("💾 Save", key=f"save_search_{paper['arxiv_id']}"):
                                    db.save_paper(
                                        title=paper['title'],
                                        authors=paper['authors'],
                                        abstract=paper.get('abstract', ''),
                                        arxiv_id=paper['arxiv_id'],
                                        pdf_url=paper['pdf_url'],
                                        published_date=paper['published_date']
                                    )
                                    st.success("Saved!")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.warning("No results found")
                except Exception as e:
                    st.error(f"Search error: {e}")
        else:
            st.info("👆 Enter a search query above")

with tab3:
    st.markdown("### 📚 My Saved Papers")
    
    # Filter options
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        show_unread = st.checkbox("Show only unread", value=False)
    with col_filter2:
        limit = st.slider("Number to show", 5, 50, 20)
    
    saved_papers = db.get_papers(is_read=0 if show_unread else None, limit=limit)
    
    if saved_papers:
        st.info(f"📊 Total: {len(saved_papers)} papers")
        
        for paper in saved_papers:
            is_read = paper.get('is_read', 0) == 1
            card_class = "paper-card-read" if is_read else "paper-card"
            
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            
            # Header with read status
            status_emoji = "✅" if is_read else "📄"
            st.markdown(f"### {status_emoji} {paper['title']}")
            st.caption(f"👥 {paper.get('authors', 'Unknown')} | 📅 {paper.get('published_date', 'N/A')}")
            
            # Display AI summary if available
            if paper.get('summary'):
                st.markdown("**🎯 AI Summary:**")
                st.info(paper['summary'])
            
            # Abstract (collapsible)
            if paper.get('abstract'):
                with st.expander("📖 Full Abstract"):
                    st.write(paper['abstract'])
            
            # Actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if paper.get('pdf_url'):
                    st.link_button("📄 PDF", paper['pdf_url'], key=f"lib_{paper['id']}")
            
            with col2:
                if not is_read:
                    if st.button("✓ Mark Read", key=f"read_{paper['id']}"):
                        db.mark_paper_read(paper['id'])
                        st.success("Marked as read!")
                        st.rerun()
                else:
                    st.caption("✅ Read")
            
            with col3:
                if not paper.get('summary'):
                    if st.button("🤖 Summarize", key=f"sum_lib_{paper['id']}"):
                        with st.spinner("Generating summary..."):
                            try:
                                summary_prompt = f"""Summarize this paper in 2-3 sentences:
                                
Title: {paper['title']}
Abstract: {paper.get('abstract', 'No abstract available')[:500]}
"""
                                response_output = session_manager.run_agent_sync(orchestrator, "user_default", summary_prompt)
                                summary = response_output
                                
                                # Update paper with summary
                                db.save_paper(
                                    title=paper['title'],
                                    authors=paper.get('authors', ''),
                                    abstract=paper.get('abstract', ''),
                                    arxiv_id=paper.get('arxiv_id', ''),
                                    pdf_url=paper.get('pdf_url', ''),
                                    published_date=paper.get('published_date', ''),
                                    summary=summary
                                )
                                st.success("Summary added!")
                                st.rerun()
                            except Exception as e:
                                import traceback
                                error_details = traceback.format_exc()
                                st.error(f"❌ Error: {str(e)}")
                                with st.expander("📋 Technical Details"):
                                    st.code(error_details)
                                st.warning("💡 This might be due to API rate limits. Please try again in a few minutes.")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.info("📭 No saved papers yet. Search for papers or use the Daily Feed!")
