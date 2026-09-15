"""
TransOrg AgentIQ Datathon - Track 3: AgriTech
Executive Insight Card Components for Dashboard
"""

import streamlit as st

SEVERITY_COLORS = {
    'High': {'bg': 'rgba(229, 62, 62, 0.1)', 'border': '#e53e3e', 'badge': '#e53e3e', 'text': '#feb2b2'},
    'Medium': {'bg': 'rgba(221, 107, 32, 0.1)', 'border': '#dd6b20', 'badge': '#dd6b20', 'text': '#fbd38d'},
    'Low': {'bg': 'rgba(56, 161, 105, 0.1)', 'border': '#38a169', 'badge': '#38a169', 'text': '#68d391'},
    'Informational': {'bg': 'rgba(74, 85, 104, 0.1)', 'border': '#4a5568', 'badge': '#4a5568', 'text': '#a0aec0'}
}

CATEGORY_ICONS = {
    'Supply': '🌾',
    'Price': '💰',
    'Logistics': '🚚',
    'Weather': '🌧️',
    'Data Quality': '🔍'
}

def render_insight_card(insight):
    """Render a single executive insight card"""
    severity = insight.get('severity', 'Informational')
    colors = SEVERITY_COLORS.get(severity, SEVERITY_COLORS['Informational'])
    category = insight.get('insight_category', 'General')
    icon = CATEGORY_ICONS.get(category, '📌')

    st.markdown(f"""
    <div style="
        background: {colors['bg']};
        border-left: 3px solid {colors['border']};
        padding: 0.75rem 1rem;
        border-radius: var(--ag-border-radius);
        margin-bottom: 0.75rem;
        box-shadow: var(--ag-shadow);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
            <span style="font-weight: 600; color: #172033; opacity: 1; font-size: 0.9rem;">
                {icon} {insight.get('insight_title', 'Insight')}
            </span>
            <span style="
                background: {colors['badge']};
                color: white;
                padding: 0.2rem 0.5rem;
                border-radius: 10px;
                font-size: 0.75rem;
                font-weight: 600;
            ">
                {severity}
            </span>
        </div>
        <div style="font-size: 0.8rem; color: #334155; opacity: 1; margin-bottom: 0.2rem;">
            <strong>Implication:</strong> {insight.get('business_implication', 'N/A')}
        </div>
        <div style="font-size: 0.75rem; color: #64748B; opacity: 1;">
            <strong>Supporting:</strong> {insight.get('supporting_data', 'N/A')}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_executive_insights_section(insights_df, limit=5):
    """Render top executive insights"""
    if insights_df is None or len(insights_df) == 0:
        st.info("No executive insights available.")
        return

    st.subheader("💡 Executive Insights & Strategic Findings")
    st.caption("Derived directly from validated analytics — not hardcoded or fabricated.")

    # Show top insights
    for _, insight in insights_df.head(limit).iterrows():
        render_insight_card(insight)
