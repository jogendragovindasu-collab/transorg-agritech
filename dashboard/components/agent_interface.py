"""
Agent Interface Component for Dashboard
Provides UI for interacting with the Agent Core
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path for agent imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.core import AgentCore


def render_agent_interface():
    """Render the complete agent interface with question input and results display."""

    # Header styling
    st.markdown("""
    <style>
    /* Agent interface prominence - Dark theme */
    .ag-agent-header {
        background: linear-gradient(135deg, var(--ag-emerald-dark) 0%, var(--ag-emerald) 100%);
        color: white;
        padding: 1rem;
        border-radius: var(--ag-border-radius);
        margin-bottom: 1rem;
        box-shadow: var(--ag-shadow);
        border: 1px solid var(--ag-border-light);
    }
    .ag-agent-header h2 {
        color: white !important;
        margin: 0;
        font-weight: 700;
        font-size: 1.3rem;
        letter-spacing: -0.01em;
    }
    .ag-agent-header p {
        color: rgba(255,255,255,0.8) !important;
        margin: 0.3rem 0 0 0;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="ag-agent-header">
        <h2>🤖 Agri Intelligence Agent</h2>
        <p>Grounded AI for agricultural supply chain analysis — deterministic analytics, transparent sources.</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize agent (cached at module level to avoid re-initialization)
    if 'agent_core' not in st.session_state:
        st.session_state.agent_core = AgentCore()

    # Six required demo questions as clickable examples
    st.subheader("Try asking:")

    demo_questions = [
        "Which crops have the highest price risk?",
        "Which mandis have high arrival volume and high price crash rates?",
        "Show Wheat arrival trends.",
        "Which warehouse has the longest transit time?",
        "Is rainfall strongly associated with arrivals?",
        "How much of the data needed cleaning?"
    ]

    # Display demo questions as buttons in a 2-column layout
    col1, col2 = st.columns(2)

    selected_question = None

    with col1:
        if st.button("📊 " + demo_questions[0], use_container_width=True):
            selected_question = demo_questions[0]
        if st.button("🌾 " + demo_questions[2], use_container_width=True):
            selected_question = demo_questions[2]
        if st.button("🌧️ " + demo_questions[4], use_container_width=True):
            selected_question = demo_questions[4]

    with col2:
        if st.button("🏪 " + demo_questions[1], use_container_width=True):
            selected_question = demo_questions[1]
        if st.button("🚚 " + demo_questions[3], use_container_width=True):
            selected_question = demo_questions[3]
        if st.button("🔍 " + demo_questions[5], use_container_width=True):
            selected_question = demo_questions[5]

    st.divider()

    # Custom question input
    st.subheader("Or ask your own question:")

    # Text input with session state to handle button clicks
    if selected_question:
        st.session_state.current_question = selected_question

    user_question = st.text_input(
        "Question",
        value=st.session_state.get('current_question', ''),
        placeholder="e.g., What is the price crash rate for Cotton?",
        label_visibility="collapsed"
    )

    analyze_clicked = st.button("🔍 Analyze", type="primary", use_container_width=False)

    # Process question
    if analyze_clicked and user_question.strip():
        with st.spinner("🤖 Agent is analyzing..."):
            try:
                result = st.session_state.agent_core.run(user_question)

                # Store result in session state for persistence
                st.session_state.last_result = result
                st.session_state.last_question = user_question

            except Exception as e:
                st.error(f"❌ Agent execution error: {e}")
                st.session_state.last_result = None

    # Display last result if available
    if 'last_result' in st.session_state and st.session_state.last_result:
        display_agent_result(
            st.session_state.last_question,
            st.session_state.last_result
        )


def display_agent_result(question: str, result: dict):
    """Display the agent's response with structured formatting."""

    st.divider()
    st.subheader("📋 Analysis Result")

    # Question echo
    st.markdown(f"**Question:** {question}")

    # Check if validated
    validated = result.get('validated', False)
    safe_fallback_used = result.get('safe_fallback_used', False)

    if safe_fallback_used:
        st.warning("⚠️ This question is outside the agent's supported scope or could not be validated.")

    payload = result.get('payload', {})
    explanation = result.get('explanation', '')

    # Main explanation
    st.markdown("---")
    st.markdown("### 💡 Answer")
    st.markdown(explanation)

    # Key metrics display
    metrics = payload.get('metrics', {})
    if metrics and isinstance(metrics, dict) and len(metrics) > 0:
        st.markdown("---")
        st.markdown("### 📊 Key Metrics")

        # Display metrics in columns (max 4 per row)
        metric_items = list(metrics.items())
        num_metrics = len(metric_items)

        if num_metrics <= 4:
            cols = st.columns(num_metrics)
            for i, (key, value) in enumerate(metric_items):
                with cols[i]:
                    # Format metric key as readable label
                    label = key.replace('_', ' ').title()
                    # Format value
                    if isinstance(value, float):
                        if abs(value) < 1:
                            formatted_value = f"{value:.3f}"
                        elif abs(value) < 100:
                            formatted_value = f"{value:.2f}"
                        else:
                            formatted_value = f"{value:,.0f}"
                    elif isinstance(value, int):
                        formatted_value = f"{value:,}"
                    else:
                        formatted_value = str(value)

                    st.metric(label, formatted_value)
        else:
            # Display as expandable table for many metrics
            with st.expander("View all metrics", expanded=True):
                metric_df_data = []
                for key, value in metric_items:
                    label = key.replace('_', ' ').title()
                    if isinstance(value, float):
                        formatted_value = f"{value:.2f}"
                    elif isinstance(value, int):
                        formatted_value = f"{value:,}"
                    else:
                        formatted_value = str(value)
                    metric_df_data.append({"Metric": label, "Value": formatted_value})

                import pandas as pd
                st.dataframe(pd.DataFrame(metric_df_data), use_container_width=True, hide_index=True)

    # Chart display
    chart_info = result.get('chart', {})
    if chart_info and chart_info.get('chart_type') != 'none':
        st.markdown("---")
        st.markdown("### 📈 Visualization")

        # Render chart using the agent's chart instructions
        render_agent_chart(chart_info, payload)

    # Business implication
    business_impl = payload.get('business_implication', '')
    if business_impl:
        st.markdown("---")
        st.markdown("### 💼 Business Implication")
        st.info(business_impl)

    # Source and methodology transparency
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📂 Source")
        source = payload.get('source', 'Not specified')
        st.code(source, language=None)

    with col2:
        st.markdown("### ⚙️ Methodology")
        limitations = payload.get('limitations', 'See agent design documentation')
        if limitations and len(limitations) > 100:
            with st.expander("View methodology notes"):
                st.caption(limitations)
        else:
            st.caption(limitations if limitations else "Standard analytics aggregation")

    # How the agent reasoned (transparency section)
    with st.expander("🔍 How the agent reasoned", expanded=False):
        st.markdown("**Detected Intent:**")
        st.code(result.get('routed', {}).get('intent', 'UNKNOWN'))

        st.markdown("**Tool Used:**")
        tool_path = result.get('routed', {}).get('tool_path', 'N/A')
        handler_name = result.get('routed', {}).get('handler_name', 'N/A')
        st.code(f"{tool_path} → {handler_name}")

        st.markdown("**Chart Type:**")
        st.code(chart_info.get('chart_type', 'none'))

        st.markdown("**Validation Status:**")
        if validated:
            st.success("✅ Result passed validation (schema, numeric sanity, source citation)")
        else:
            st.warning("⚠️ Result did not pass full validation")

        st.markdown("**Source Dataset:**")
        st.code(payload.get('source', 'Not specified'))


def render_agent_chart(chart_info: dict, payload: dict):
    """Render the appropriate chart based on agent's chart selection."""

    chart_type = chart_info.get('chart_type', 'none')

    # Import chart rendering utilities
    from dashboard.components.agent_chart_renderer import render_chart_from_agent

    try:
        fig = render_chart_from_agent(chart_type, payload, chart_info)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"📊 Chart type '{chart_type}' rendering not yet implemented. Showing data summary instead.")

            # Fallback: show metrics as table
            if payload.get('metrics'):
                import pandas as pd
                metric_data = []
                for k, v in payload['metrics'].items():
                    metric_data.append({"Metric": k.replace('_', ' ').title(), "Value": v})
                st.dataframe(pd.DataFrame(metric_data), use_container_width=True, hide_index=True)

    except Exception as e:
        st.warning(f"⚠️ Could not render chart: {e}")
        st.caption("Displaying metrics in table format instead.")

        # Fallback display
        if payload.get('metrics'):
            import pandas as pd
            metric_data = []
            for k, v in payload['metrics'].items():
                metric_data.append({"Metric": k.replace('_', ' ').title(), "Value": v})
            st.dataframe(pd.DataFrame(metric_data), use_container_width=True, hide_index=True)
