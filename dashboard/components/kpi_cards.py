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
        padding: 0.75rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(15,61,39,0.06), 0 1px 2px rgba(15,61,39,0.04);
        border: 1px solid #dde5db;
        margin-bottom: 0;
        transition: box-shadow 0.2s ease, transform 0.1s ease;
    " onmouseover="this.style.transform='translateY(-1px)';this.style.boxShadow='0 4px 12px rgba(15,61,39,0.1)';"
       onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 2px 8px rgba(15,61,39,0.06), 0 1px 2px rgba(15,61,39,0.04)';"
    >
        <div style="font-size: 0.75rem; color: #2d5a3d; text-transform: uppercase; font-weight: 600; letter-spacing: 0.02em;">
            {icon + ' ' if icon else ''}{title}
        </div>
        <div style="font-size: 1.5rem; font-weight: 800; color: #1a4d2e; margin: 0.2rem 0; letter-spacing: -0.01em;">
            {value}
        </div>
        {f'<div style="font-size: 0.75rem; color: #556b5e;">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_hero_kpis(kpis):
    """Render the top 6 hero KPI cards in responsive columns (3x2 grid on desktop, 2x3 or 1x6 on narrow)"""
    # Use responsive column layout: 3+3 split to avoid 6 narrow squeezed cards
    row1 = st.columns(3)
    row2 = st.columns(3)

    card_data = [
        ("Total Arrivals", f"{kpis['total_arrivals_qtl']:,.0f} Qtl", "Analyzed arrival volume", "🌾"),
        ("Price Crash Rate", f"{kpis['price_crash_rate']:.1f}%", "Records below MSP", "⚠️"),
        ("Avg Modal Price", f"Rs. {kpis['avg_modal_price']:,.0f}", "Per quintal average", "💰"),
        ("Avg MSP", f"Rs. {kpis['avg_msp']:,.0f}", "Govt support price", "🛡️"),
        ("Active Mandis", f"{kpis['active_mandis']}", "With arrival data", "🏛️"),
        ("Avg Transit Time", f"{kpis['avg_transit_hours']:.1f} hrs", f"Median: {kpis['median_transit_hours']:.1f} hrs", "🚚"),
    ]
    for i, (title, value, subtitle, icon) in enumerate(card_data):
        with (row1[i] if i < 3 else row2[i - 3]):
            render_kpi_card(title=title, value=value, subtitle=subtitle, icon=icon)
