"""
TransOrg AgentIQ Datathon - Track 3: AgriTech
KPI Card Components for Dashboard
"""

import streamlit as st

def render_kpi_card(title, value, subtitle=None, delta=None, delta_color="normal", icon=None):
    """Render a single KPI card with optional subtitle and delta"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #ffffff 0%, #f8fdf8 100%);
        padding: 1.25rem;
        border-radius: 14px;
        box-shadow: 0 4px 16px rgba(15,61,39,0.08), 0 1px 3px rgba(15,61,39,0.04);
        border: 1px solid #dde5db;
        margin-bottom: 1rem;
        transition: box-shadow 0.2s ease, transform 0.15s ease;
    " onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 24px rgba(15,61,39,0.12)';"
       onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 16px rgba(15,61,39,0.08), 0 1px 3px rgba(15,61,39,0.04)';"
    >
        <div style="font-size: 0.85rem; color: #2d5a3d; text-transform: uppercase; font-weight: 600; letter-spacing: 0.03em;">
            {icon + ' ' if icon else ''}{title}
        </div>
        <div style="font-size: 1.9rem; font-weight: 800; color: #1a4d2e; margin: 0.35rem 0; letter-spacing: -0.02em;">
            {value}
        </div>
        {f'<div style="font-size: 0.85rem; color: #556b5e;">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_hero_kpis(kpis):
    """Render the top 6 hero KPI cards in a 3x2 grid"""
    col1, col2, col3 = st.columns(3)

    with col1:
        render_kpi_card(
            title="Total Arrivals",
            value=f"{kpis['total_arrivals_qtl']:,.0f} Qtl",
            subtitle="Analyzed arrival volume",
            icon="🌾"
        )
        render_kpi_card(
            title="Price Crash Rate",
            value=f"{kpis['price_crash_rate']:.1f}%",
            subtitle="Records below MSP",
            icon="⚠️"
        )

    with col2:
        render_kpi_card(
            title="Avg Modal Price",
            value=f"Rs. {kpis['avg_modal_price']:,.0f}",
            subtitle="Per quintal average",
            icon="💰"
        )
        render_kpi_card(
            title="Avg MSP",
            value=f"Rs. {kpis['avg_msp']:,.0f}",
            subtitle="Govt support price",
            icon="🛡️"
        )

    with col3:
        render_kpi_card(
            title="Active Mandis",
            value=f"{kpis['active_mandis']}",
            subtitle="With arrival data",
            icon="🏛️"
        )
        render_kpi_card(
            title="Avg Transit Time",
            value=f"{kpis['avg_transit_hours']:.1f} hrs",
            subtitle=f"Median: {kpis['median_transit_hours']:.1f} hrs",
            icon="🚚"
        )
