"""
TransOrg AgentIQ Datathon - Track 3: AgriTech
Executive Insight Card Components for Dashboard
"""

import streamlit as st

SEVERITY_COLORS = {
    'High': {'bg': '#fff5f5', 'border': '#e53e3e', 'badge': '#e53e3e', 'text': '#9b2c2c'},
    'Medium': {'bg': '#fffaf0', 'border': '#dd6b20', 'badge': '#dd6b20', 'text': '#9c4221'},
    'Low': {'bg': '#f0fff4', 'border': '#38a169', 'badge': '#38a169', 'text': '#276749'},
    'Informational': {'bg': '#f7fafc', 'border': '#4a5568', 'badge': '#4a5568', 'text': '#2d3748'}
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
        border-left: 4px solid {colors['border']};
        padding: 1rem 1.25rem;
        border-radius: 4px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 700; color: #2d3748; font-size: 0.95rem;">
                {icon} {insight.get('insight_title', 'Insight')}
            </span>
            <span style="
                background: {colors['badge']};
                color: white;
                padding: 0.15rem 0.5rem;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 600;
            ">
                {severity}
            </span>
        </div>
        <div style="font-size: 0.85rem; color: #4a5568; margin-bottom: 0.25rem;">
            <strong>Implication:</strong> {insight.get('business_implication', 'N/A')}
        </div>
        <div style="font-size: 0.8rem; color: #718096;">
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
