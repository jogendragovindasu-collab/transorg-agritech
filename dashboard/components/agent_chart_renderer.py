"""
Agent Chart Renderer
Converts agent chart instructions into actual Plotly visualizations.
No arbitrary code execution - only controlled rendering of supported chart types.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path

# Light analytical chart theme (visible data surfaces, dark readable text)
CHART_THEME = {
    'bg_light': '#FFFFFF',
    'text_title': '#172033',
    'text_axis': '#526070',
    'text_legend': '#526070',
    'grid': '#E5EAF0',
    'border': '#26384A',
    'emerald': '#22C98A',
    'warning': '#F5B84B',
    'danger': '#F45B69',
    'blue': '#5B8DEF',
}

ANALYTICS_DIR = Path('analytics')


def render_chart_from_agent(chart_type: str, payload: dict, chart_info: dict):
    chart_renderers = {
        'scatter_plot': render_scatter_plot,
        'line_time_series': render_line_chart,
        'bar_transit': render_bar_chart,
        'horizontal_bar': render_horizontal_bar,
        'dual_axis': render_dual_axis_chart,
        'transformation_bar': render_transformation_bar,
        'kpi_cards': None,
        'priority_table': None,
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


def _base_light_layout(fig, title, height=500):
    fig.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(family='Inter', color='#172033'),
        title_font=dict(color='#172033', size=14),
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
            font=dict(color='#172033'), bgcolor='#FFFFFF', bordercolor='#26384A', borderwidth=1
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=height,
        title=title,
    )
    # Light grid lines and visible axes
    fig.update_xaxes(
        gridcolor='#E5EAF0', zerolinecolor='#E5EAF0',
        tickfont=dict(color='#526070'),
        showline=True, linecolor='#D1D5DB', linewidth=1
    )
    fig.update_yaxes(
        gridcolor='#E5EAF0', zerolinecolor='#E5EAF0',
        tickfont=dict(color='#526070'),
        showline=True, linecolor='#D1D5DB', linewidth=1
    )
    return fig


def render_scatter_plot(payload: dict, chart_info: dict):
    intent = payload.get('intent', '')
    if intent == 'PRICE_RISK':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'crop_kpis.csv')
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['total_arrivals_qtl'],
                y=df['price_crash_rate'],
                mode='markers+text',
                marker=dict(
                    size=df['farmer_count'] / 100,
                    color=df['price_crash_rate'],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Crash Rate %", tickfont=dict(color='#526070'))
                ),
                text=df['crop_name'],
                textposition='top center',
                textfont=dict(color='#172033', size=10),
                hovertemplate='<b>%{text}</b><br>Arrivals: %{x:,.0f} Qtl<br>Crash Rate: %{y:.1f}%<extra></extra>'
            ))
            median_vol = df['total_arrivals_qtl'].median()
            fig.add_vline(x=median_vol, line_dash="dash", line_color="#526070", opacity=0.5)
            fig.add_hline(y=30, line_dash="dash", line_color="#F45B69", opacity=0.7,
                          annotation_text="30% Risk Threshold", annotation_font=dict(color='#172033'))
            fig = _base_light_layout(fig, "Price Vulnerability Matrix: Arrival Volume vs Crash Rate", height=500)
            fig.update_layout(
                xaxis_title="Total Arrivals (Qtl)",
                yaxis_title="Price Crash Rate (%)",
                xaxis_title_font=dict(color='#526070'),
                yaxis_title_font=dict(color='#526070'),
                hovermode='closest',
            )
            return fig
        except Exception as e:
            print(f"Could not render price risk scatter: {e}")
            return None
    return None


def render_line_chart(payload: dict, chart_info: dict):
    intent = payload.get('intent', '')
    if intent == 'SUPPLY_TREND':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'daily_kpis.csv')
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df['rolling_avg'] = df['total_arrival_qty_qtl'].rolling(window=7, min_periods=1).mean()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['total_arrival_qty_qtl'],
                mode='lines',
                name='Daily Arrivals',
                line=dict(color='#22C98A', width=2),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Arrivals: %{y:,.0f} Qtl<extra></extra>'
            ))
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['rolling_avg'],
                mode='lines',
                name='7-Day Trend',
                line=dict(color='#F5B84B', width=2, dash='dash'),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>7-Day Avg: %{y:,.0f} Qtl<extra></extra>'
            ))
            fig = _base_light_layout(fig, "Daily Arrival Trends", height=500)
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Arrivals (Qtl)",
                xaxis_title_font=dict(color='#526070'),
                yaxis_title_font=dict(color='#526070'),
                hovermode='x unified',
            )
            return fig
        except Exception as e:
            print(f"Could not render supply trend line chart: {e}")
            return None
    return None


def render_bar_chart(payload: dict, chart_info: dict):
    intent = payload.get('intent', '')
    if intent == 'LOGISTICS':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'warehouse_kpis.csv')
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
                    colorbar=dict(title="Hours", tickfont=dict(color='#526070'))
                ),
                text=df['median_transit_hours'].apply(lambda x: f"{x:.1f}h"),
                textposition='outside',
                textfont=dict(color='#172033', size=9),
                hovertemplate='<b>%{y}</b><br>Median Transit: %{x:.1f} hours<extra></extra>'
            ))
            fig = _base_light_layout(fig, "Top 10 Warehouses by Median Transit Time", height=500)
            fig.update_layout(
                xaxis_title="Median Transit Hours",
                yaxis_title="Warehouse",
                xaxis_title_font=dict(color='#526070'),
                yaxis_title_font=dict(color='#526070'),
                yaxis=dict(autorange='reversed'),
            )
            return fig
        except Exception as e:
            print(f"Could not render logistics bar chart: {e}")
            return None
    return None


def render_horizontal_bar(payload: dict, chart_info: dict):
    intent = payload.get('intent', '')
    if intent == 'MANDI_ANALYSIS':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'mandi_kpis.csv')
            df = df.sort_values('total_arrival_qty_qtl', ascending=True).tail(10)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=df['mandi_id'],
                x=df['total_arrival_qty_qtl'],
                orientation='h',
                marker=dict(color='#22C98A'),
                text=df['total_arrival_qty_qtl'].apply(lambda x: f"{x:,.0f}"),
                textposition='outside',
                textfont=dict(color='#172033', size=9),
                hovertemplate='<b>%{y}</b><br>Arrivals: %{x:,.0f} Qtl<extra></extra>'
            ))
            fig = _base_light_layout(fig, "Top 10 Mandis by Arrival Volume", height=500)
            fig.update_layout(
                xaxis_title="Total Arrivals (Qtl)",
                yaxis_title="Mandi ID",
                xaxis_title_font=dict(color='#526070'),
                yaxis_title_font=dict(color='#526070'),
            )
            return fig
        except Exception as e:
            print(f"Could not render mandi horizontal bar: {e}")
            return None
    return None


def render_dual_axis_chart(payload: dict, chart_info: dict):
    intent = payload.get('intent', '')
    if intent == 'WEATHER':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'weather_arrival_analysis.csv')
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['date'],
                y=df['total_rainfall_mm'],
                name='Rainfall (mm)',
                marker=dict(color='#5B8DEF', opacity=0.6),
                yaxis='y',
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Rainfall: %{y:.1f} mm<extra></extra>'
            ))
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['total_arrivals_qtl'],
                name='Arrivals (Qtl)',
                mode='lines+markers',
                line=dict(color='#22C98A', width=2),
                yaxis='y2',
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Arrivals: %{y:,.0f} Qtl<extra></extra>'
            ))
            corr = df['total_rainfall_mm'].corr(df['total_arrivals_qtl'])
            fig = _base_light_layout(fig, f"Rainfall vs Arrivals (Date-Level) — Correlation: r = {corr:.2f}", height=500)
            fig.update_layout(
                xaxis=dict(title="Date", titlefont=dict(color='#526070')),
                yaxis=dict(
                    title="Rainfall (mm)", titlefont=dict(color='#5B8DEF'), tickfont=dict(color='#526070'),
                    side='left', gridcolor='#E5EAF0', zerolinecolor='#E5EAF0', showline=True, linecolor='#D1D5DB'
                ),
                yaxis2=dict(
                    title="Arrivals (Qtl)", titlefont=dict(color='#22C98A'), tickfont=dict(color='#526070'),
                    overlaying='y', side='right', gridcolor='#E5EAF0', zerolinecolor='#E5EAF0', showline=True, linecolor='#D1D5DB'
                ),
                hovermode='x unified',
            )
            return fig
        except Exception as e:
            print(f"Could not render weather dual-axis chart: {e}")
            return None
    return None


def render_transformation_bar(payload: dict, chart_info: dict):
    intent = payload.get('intent', '')
    if intent == 'DATA_QUALITY':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'data_quality_summary.csv')
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['dataset'],
                y=df['valid_quantity'],
                name='Valid Records',
                marker=dict(color='#22C98A'),
                text=df['valid_quantity'].apply(lambda x: f"{x:,}"),
                textposition='inside',
                textfont=dict(color='#FFFFFF', size=10),
                hovertemplate='<b>%{x}</b><br>Valid: %{y:,}<extra></extra>'
            ))
            excluded = df['total_records'] - df['valid_quantity']
            fig.add_trace(go.Bar(
                x=df['dataset'],
                y=excluded,
                name='Excluded Records',
                marker=dict(color='#F45B69'),
                text=excluded.apply(lambda x: f"{x:,}"),
                textposition='inside',
                textfont=dict(color='#FFFFFF', size=10),
                hovertemplate='<b>%{x}</b><br>Excluded: %{y:,}<extra></extra>'
            ))
            fig = _base_light_layout(fig, "Data Cleaning Impact: Before → After", height=500)
            fig.update_layout(
                xaxis_title="Dataset", yaxis_title="Record Count",
                xaxis_title_font=dict(color='#526070'), yaxis_title_font=dict(color='#526070'),
                barmode='stack',
            )
            return fig
        except Exception as e:
            print(f"Could not render data quality bar chart: {e}")
            return None
    return None


def render_donut_chart(payload: dict, chart_info: dict):
    intent = payload.get('intent', '')
    if intent == 'CROP_ANALYSIS':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'crop_kpis.csv')
            df = df.sort_values('total_arrivals_qtl', ascending=False)
            top_crops = df.head(8)
            other_sum = df.tail(len(df) - 8)['total_arrivals_qtl'].sum() if len(df) > 8 else 0
            if other_sum > 0:
                other_row = pd.DataFrame({'crop_name': ['Other'], 'total_arrivals_qtl': [other_sum]})
                plot_df = pd.concat([top_crops[['crop_name', 'total_arrivals_qtl']], other_row])
            else:
                plot_df = top_crops[['crop_name', 'total_arrivals_qtl']]
            fig = go.Figure(data=[go.Pie(
                labels=plot_df['crop_name'],
                values=plot_df['total_arrivals_qtl'],
                hole=0.4,
                hovertemplate='<b>%{label}</b><br>Arrivals: %{value:,.0f} Qtl<br>Share: %{percent}<extra></extra>'
            )])
            fig = _base_light_layout(fig, "Crop Distribution by Arrival Volume", height=500)
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont=dict(color='#172033', size=10)
            )
            return fig
        except Exception as e:
            print(f"Could not render crop donut chart: {e}")
            return None
    return None


def render_grouped_bar(payload: dict, chart_info: dict):
    intent = payload.get('intent', '')
    if intent == 'PRICE_MSP':
        try:
            df = pd.read_csv(ANALYTICS_DIR / 'crop_kpis.csv')
            df = df.sort_values('price_crash_rate', ascending=False).head(10)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['crop_name'],
                y=df['avg_modal_price'],
                name='Modal Price',
                marker=dict(color='#5B8DEF'),
                hovertemplate='<b>%{x}</b><br>Modal Price: ₹%{y:,.0f}<extra></extra>',
                text=df['avg_modal_price'].apply(lambda x: f"₹{x:,.0f}"),
                textposition='auto',
                textfont=dict(color='#172033', size=9)
            ))
            fig.add_trace(go.Bar(
                x=df['crop_name'],
                y=df['avg_msp'],
                name='MSP',
                marker=dict(color='#22C98A'),
                hovertemplate='<b>%{x}</b><br>MSP: ₹%{y:,.0f}<extra></extra>',
                text=df['avg_msp'].apply(lambda x: f"₹{x:,.0f}"),
                textposition='auto',
                textfont=dict(color='#172033', size=9)
            ))
            fig = _base_light_layout(fig, "Modal Price vs MSP Comparison (Top 10 by Crash Rate)", height=500)
            fig.update_layout(
                xaxis_title="Crop", yaxis_title="Price (₹)",
                xaxis_title_font=dict(color='#526070'), yaxis_title_font=dict(color='#526070'),
                barmode='group',
            )
            return fig
        except Exception as e:
            print(f"Could not render price vs MSP grouped bar: {e}")
            return None
    return None
