"""
Agent Chart Renderer
Converts agent chart instructions into actual Plotly visualizations.
No arbitrary code execution - only controlled rendering of supported chart types.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path

ANALYTICS_DIR = Path('analytics')


def render_chart_from_agent(chart_type: str, payload: dict, chart_info: dict):
    """
    Render a Plotly figure based on the agent's chart selection.

    Args:
        chart_type: Chart type from agent/chart_selector.py
        payload: Validated tool result payload
        chart_info: Chart metadata from select_chart()

    Returns:
        Plotly Figure or None
    """

    # Map chart types to rendering functions
    chart_renderers = {
        'scatter_plot': render_scatter_plot,
        'line_time_series': render_line_chart,
        'bar_transit': render_bar_chart,
        'horizontal_bar': render_horizontal_bar,
        'dual_axis': render_dual_axis_chart,
        'transformation_bar': render_transformation_bar,
        'kpi_cards': None,  # KPI cards handled separately
        'priority_table': None,  # Tables handled separately
        'donut': render_donut_chart,
        'grouped_bar': render_grouped_bar,
    }

    renderer = chart_renderers.get(chart_type)

    if renderer is None:
        return None

    try:
        return renderer(payload, chart_info)
    except Exception as e:
        print(f"Chart rendering error for {chart_type}: {e}")
        return None


def render_scatter_plot(payload: dict, chart_info: dict):
    """Render scatter plot for price risk analysis."""

    intent = payload.get('intent', '')

    # Load appropriate data based on intent
    if intent == 'PRICE_RISK':
        # Try to load crop KPIs for price risk scatter
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'crop_kpis.csv')

            # Price vulnerability matrix: volume vs crash rate
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df['total_arrivals_qtl'],
                y=df['price_crash_rate'],
                mode='markers+text',
                marker=dict(
                    size=df['farmer_count'] / 100,  # Size by farmer count
                    color=df['price_crash_rate'],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Crash Rate %")
                ),
                text=df['crop_name'],
                textposition='top center',
                hovertemplate='<b>%{text}</b><br>Arrivals: %{x:,.0f} Qtl<br>Crash Rate: %{y:.1f}%<extra></extra>'
            ))

            fig.update_layout(
                title="Price Vulnerability Matrix: Arrival Volume vs Crash Rate",
                title_font=dict(color='#1a4d2e', size=15, family='Inter'),
                font=dict(family='Inter'),
                plot_bgcolor='rgba(255,255,255,0)',
                paper_bgcolor='rgba(255,255,255,0)',
                xaxis_title="Total Arrivals (Qtl)",
                xaxis_title_font=dict(color='#556b5e'),
                yaxis_title="Price Crash Rate (%)",
                yaxis_title_font=dict(color='#556b5e'),
                hovermode='closest',
                height=500,
                margin=dict(l=50, r=40, t=80, b=50)
            )

            return fig

        except Exception as e:
            print(f"Could not render price risk scatter: {e}")
            return None

    return None


def render_line_chart(payload: dict, chart_info: dict):
    """Render line chart for time series (supply trends)."""

    intent = payload.get('intent', '')

    if intent == 'SUPPLY_TREND':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'daily_kpis.csv')
            df['date'] = pd.to_datetime(df['date'])

            # Calculate 7-day rolling average
            df = df.sort_values('date')
            df['rolling_avg'] = df['total_arrival_qty_qtl'].rolling(window=7, min_periods=1).mean()

            fig = go.Figure()

            # Daily arrivals
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['total_arrival_qty_qtl'],
                mode='lines',
                name='Daily Arrivals',
                line=dict(color='#3b82f6', width=1),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Arrivals: %{y:,.0f} Qtl<extra></extra>'
            ))

            # Rolling average trend
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['rolling_avg'],
                mode='lines',
                name='7-Day Trend',
                line=dict(color='#ef4444', width=2, dash='dash'),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>7-Day Avg: %{y:,.0f} Qtl<extra></extra>'
            ))

            fig.update_layout(
                title="Daily Arrival Trends",
                title_font=dict(color='#1a4d2e', size=15, family='Inter'),
                font=dict(family='Inter'),
                plot_bgcolor='rgba(255,255,255,0)',
                paper_bgcolor='rgba(255,255,255,0)',
                xaxis_title="Date",
                xaxis_title_font=dict(color='#556b5e'),
                yaxis_title="Arrivals (Qtl)",
                yaxis_title_font=dict(color='#556b5e'),
                hovermode='x unified',
                height=500,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(color='#1a1a2e')),
                margin=dict(l=50, r=40, t=80, b=50)
            )

            return fig

        except Exception as e:
            print(f"Could not render supply trend line chart: {e}")
            return None

    return None


def render_bar_chart(payload: dict, chart_info: dict):
    """Render bar chart for logistics/warehouse transit times."""

    intent = payload.get('intent', '')

    if intent == 'LOGISTICS':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'warehouse_kpis.csv')

            # Sort by median transit hours (descending) and take top 10
            df = df.sort_values('median_transit_hours', ascending=False).head(10)

            fig = go.Figure()

            fig.add_trace(go.Bar(
                y=df['destination_warehouse'],
                x=df['median_transit_hours'],
                orientation='h',
                marker=dict(
                    color=df['median_transit_hours'],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Hours")
                ),
                text=df['median_transit_hours'].apply(lambda x: f"{x:.1f}h"),
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Median Transit: %{x:.1f} hours<extra></extra>'
            ))

            fig.update_layout(
                title="Top 10 Warehouses by Median Transit Time",
                xaxis_title="Median Transit Hours",
                yaxis_title="Warehouse",
                height=500,
                yaxis=dict(autorange='reversed')
            )

            return fig

        except Exception as e:
            print(f"Could not render logistics bar chart: {e}")
            return None

    return None


def render_horizontal_bar(payload: dict, chart_info: dict):
    """Render horizontal bar chart for mandi analysis."""

    intent = payload.get('intent', '')

    if intent == 'MANDI_ANALYSIS':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'mandi_kpis.csv')

            # Sort by arrival volume and take top 10
            df = df.sort_values('total_arrival_qty_qtl', ascending=True).tail(10)

            fig = go.Figure()

            fig.add_trace(go.Bar(
                y=df['mandi_id'],
                x=df['total_arrival_qty_qtl'],
                orientation='h',
                marker=dict(color='#10b981'),
                text=df['total_arrival_qty_qtl'].apply(lambda x: f"{x:,.0f}"),
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Arrivals: %{x:,.0f} Qtl<extra></extra>'
            ))

            fig.update_layout(
                title="Top 10 Mandis by Arrival Volume",
                xaxis_title="Total Arrivals (Qtl)",
                yaxis_title="Mandi ID",
                height=500
            )

            return fig

        except Exception as e:
            print(f"Could not render mandi horizontal bar: {e}")
            return None

    return None


def render_dual_axis_chart(payload: dict, chart_info: dict):
    """Render dual-axis chart for weather-arrival correlation."""

    intent = payload.get('intent', '')

    if intent == 'WEATHER':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'weather_arrival_analysis.csv')
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            fig = go.Figure()

            # Rainfall bars (left axis)
            fig.add_trace(go.Bar(
                x=df['date'],
                y=df['total_rainfall_mm'],
                name='Rainfall (mm)',
                marker=dict(color='#3b82f6', opacity=0.6),
                yaxis='y',
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Rainfall: %{y:.1f} mm<extra></extra>'
            ))

            # Arrivals line (right axis)
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['total_arrivals_qtl'],
                name='Arrivals (Qtl)',
                mode='lines+markers',
                line=dict(color='#10b981', width=2),
                yaxis='y2',
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Arrivals: %{y:,.0f} Qtl<extra></extra>'
            ))

            # Calculate correlation for subtitle
            corr = df['total_rainfall_mm'].corr(df['total_arrivals_qtl'])

            fig.update_layout(
                title=f"Rainfall vs Arrivals (Date-Level) — Correlation: r = {corr:.2f}",
                xaxis=dict(title="Date"),
                yaxis=dict(
                    title="Rainfall (mm)",
                    side='left'
                ),
                yaxis2=dict(
                    title="Arrivals (Qtl)",
                    side='right',
                    overlaying='y'
                ),
                hovermode='x unified',
                height=500,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )

            return fig

        except Exception as e:
            print(f"Could not render weather dual-axis chart: {e}")
            return None

    return None


def render_transformation_bar(payload: dict, chart_info: dict):
    """Render transformation/data quality bar chart."""

    intent = payload.get('intent', '')

    if intent == 'DATA_QUALITY':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'data_quality_summary.csv')

            fig = go.Figure()

            # Valid records
            fig.add_trace(go.Bar(
                x=df['dataset'],
                y=df['valid_quantity'],
                name='Valid Records',
                marker=dict(color='#10b981'),
                text=df['valid_quantity'].apply(lambda x: f"{x:,}"),
                textposition='inside',
                hovertemplate='<b>%{x}</b><br>Valid: %{y:,}<extra></extra>'
            ))

            # Excluded records
            excluded = df['total_records'] - df['valid_quantity']
            fig.add_trace(go.Bar(
                x=df['dataset'],
                y=excluded,
                name='Excluded Records',
                marker=dict(color='#ef4444'),
                text=excluded.apply(lambda x: f"{x:,}"),
                textposition='inside',
                hovertemplate='<b>%{x}</b><br>Excluded: %{y:,}<extra></extra>'
            ))

            fig.update_layout(
                title="Data Cleaning Impact: Before → After",
                xaxis_title="Dataset",
                yaxis_title="Record Count",
                barmode='stack',
                height=500,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )

            return fig

        except Exception as e:
            print(f"Could not render data quality bar chart: {e}")
            return None

    return None


def render_donut_chart(payload: dict, chart_info: dict):
    """Render donut chart for crop distribution."""

    intent = payload.get('intent', '')

    if intent == 'CROP_ANALYSIS':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'crop_kpis.csv')

            # Sort by arrivals and take top 8, group rest as "Other"
            df = df.sort_values('total_arrivals_qtl', ascending=False)
            top_crops = df.head(8)
            other_sum = df.tail(len(df) - 8)['total_arrivals_qtl'].sum() if len(df) > 8 else 0

            if other_sum > 0:
                other_row = pd.DataFrame({
                    'crop_name': ['Other'],
                    'total_arrivals_qtl': [other_sum]
                })
                plot_df = pd.concat([top_crops[['crop_name', 'total_arrivals_qtl']], other_row])
            else:
                plot_df = top_crops[['crop_name', 'total_arrivals_qtl']]

            fig = go.Figure(data=[go.Pie(
                labels=plot_df['crop_name'],
                values=plot_df['total_arrivals_qtl'],
                hole=0.4,
                hovertemplate='<b>%{label}</b><br>Arrivals: %{value:,.0f} Qtl<br>Share: %{percent}<extra></extra>'
            )])

            fig.update_layout(
                title="Crop Distribution by Arrival Volume",
                height=500
            )

            return fig

        except Exception as e:
            print(f"Could not render crop donut chart: {e}")
            return None

    return None


def render_grouped_bar(payload: dict, chart_info: dict):
    """Render grouped bar chart for price vs MSP comparison."""

    intent = payload.get('intent', '')

    if intent == 'PRICE_MSP':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'crop_kpis.csv')

            # Sort by price crash rate and take top 10
            df = df.sort_values('price_crash_rate', ascending=False).head(10)

            fig = go.Figure()

            # Modal price
            fig.add_trace(go.Bar(
                x=df['crop_name'],
                y=df['avg_modal_price'],
                name='Modal Price',
                marker=dict(color='#3b82f6'),
                hovertemplate='<b>%{x}</b><br>Modal Price: ₹%{y:,.0f}<extra></extra>'
            ))

            # MSP
            fig.add_trace(go.Bar(
                x=df['crop_name'],
                y=df['avg_msp'],
                name='MSP',
                marker=dict(color='#10b981'),
                hovertemplate='<b>%{x}</b><br>MSP: ₹%{y:,.0f}<extra></extra>'
            ))

            fig.update_layout(
                title="Modal Price vs MSP Comparison (Top 10 by Crash Rate)",
                xaxis_title="Crop",
                yaxis_title="Price (₹)",
                barmode='group',
                height=500,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )

            return fig

        except Exception as e:
            print(f"Could not render price vs MSP grouped bar: {e}")
            return None

    return None
