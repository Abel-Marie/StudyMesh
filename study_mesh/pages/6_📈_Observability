import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.observability.logger import Logger
from src.observability.metrics import MetricsCollector

st.set_page_config(page_title="Observability", page_icon="📈", layout="wide")

# Initialize
logger = Logger()
metrics = MetricsCollector()

st.title("📈 Observability Dashboard")

st.markdown("""
This page shows logging, tracing, and metrics for the AI Productivity Planner.
""")

# Tabs
tab1, tab2 = st.tabs(["📋 Logs", "📊 Metrics"])

with tab1:
    st.markdown("### Recent Logs")
    
    try:
        logs = logger.get_recent_logs(lines=50)
        
        if logs:
            # Display in code block
            log_text = "".join(logs)
            st.code(log_text, language="log")
            
            # Log statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                info_logs = len([l for l in logs if "INFO" in l])
                st.metric("INFO", info_logs)
            with col2:
                error_logs = len([l for l in logs if "ERROR" in l])
                st.metric("ERROR", error_logs)
            with col3:
                debug_logs = len([l for l in logs if "DEBUG" in l])
                st.metric("DEBUG", debug_logs)
        else:
            st.info("No logs yet. Logs will appear as you use the application.")
    except Exception as e:
        st.error(f"Error reading logs: {e}")
    
    # Manual log entry
    st.markdown("---")
    st.markdown("### Add Manual Log")
    
    with st.form("manual_log"):
        log_type = st.selectbox("Type", ["INFO", "ERROR", "DEBUG"])
        log_message = st.text_input("Message")
        
        if st.form_submit_button("Add Log"):
            if log_message:
                if log_type == "INFO":
                    logger.logger.info(log_message)
                elif log_type == "ERROR":
                    logger.logger.error(log_message)
                else:
                    logger.logger.debug(log_message)
                st.success("Log added!")
                st.rerun()

with tab2:
    st.markdown("### Application Metrics")
    
    all_metrics = metrics.get_all_metrics()
    
    if all_metrics:
        # Display metrics in cards
        cols = st.columns(3)
        
        for i, (metric_name, metric_data) in enumerate(all_metrics.items()):
            with cols[i % 3]:
                if isinstance(metric_data, dict):
                    st.metric(
                        metric_name.replace("_", " ").title(),
                        f"{metric_data.get('latest', 0):.2f}",
                        delta=f"Avg: {metric_data.get('average', 0):.2f}"
                    )
                else:
                    st.metric(
                        metric_name.replace("_", " ").title(),
                        metric_data
                    )
    else:
        st.info("No metrics collected yet. Metrics will appear as you use the application.")
    
    # Track a test metric
    st.markdown("---")
    st.markdown("### Track Test Metric")
    
    with st.form("track_metric"):
        metric_name = st.text_input("Metric Name")
        metric_value = st.number_input("Value", value=0.0)
        
        if st.form_submit_button("Track"):
            if metric_name:
                metrics.track_metric(metric_name, metric_value)
                st.success(f"Tracked {metric_name} = {metric_value}")
                st.rerun()

st.markdown("---")
st.markdown("### 🎯 Capstone Concept: Observability")
st.info("""
This page demonstrates **Observability** through:
- **Logging**: All agent calls, user actions, and errors are logged
- **Metrics**: Performance and usage metrics are tracked
- **Tracing**: Agent execution flow is monitored

This helps debug issues, monitor performance, and understand user behavior.
""")
