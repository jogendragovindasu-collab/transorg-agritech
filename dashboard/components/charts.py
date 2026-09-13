"""
TransOrg AgentIQ Datathon - Track 3: AgriTech
Plotly Chart Components for Dashboard
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def chart_daily_arrivals(daily_df, selected_crop=None):
    """Line chart of daily arrivals with optional moving average"""
    if daily_df is None or len(daily_df) == 0:
        return go.Figure()

    df = daily_df.copy().sort_values('date')

    # Add 7-day rolling mean
    df['rolling_7d'] = df['daily_arrivals_qtl'].rolling(window=7, min_periods=1).mean()

    fig = go.Figure()

    # Actual daily
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['daily_arrivals_qtl'],
        mode='lines',
        name='Daily Arrivals',
        line=dict(color='#90cdf4', width=1),
        opacity=0.6
    ))

    # 7-day moving average
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['rolling_7d'],
        mode='lines',
        name='7-Day Trend',
        line=dict(color='#3182ce', width=2.5)
    ))

    # Deep green palette for charts
    fig.update_layout(
        title='Daily Arrival Volume (Quintals)',
        title_font=dict(color='#1a4d2e', size=16, family='Inter'),
        xaxis_title='Date',
        xaxis_title_font=dict(color='#556b5e'),
        yaxis_title='Arrivals (Qtl)',
        yaxis_title_font=dict(color='#556b5e'),
        font=dict(family='Inter'),
        plot_bgcolor='rgba(255,255,255,0)',
        paper_bgcolor='rgba(255,255,255,0)',
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(color='#1a1a2e')),
        margin=dict(l=50, r=40, t=70, b=50),
        height=420
    )

    return fig

def chart_supply_concentration(mandi_kpis_df, top_n=10):
    """Horizontal bar chart for top mandis by arrival volume"""
    if mandi_kpis_df is None or len(mandi_kpis_df) == 0:
        return go.Figure()

    top_mandis = mandi_kpis_df.nlargest(top_n, 'total_arrival_qty_qtl').sort_values('total_arrival_qty_qtl')

    colors = ['#3182ce' if i >= (top_n - 5) else '#a0aec0' for i in range(len(top_mandis))]

    fig = go.Figure(go.Bar(
        x=top_mandis['total_arrival_qty_qtl'],
        y=top_mandis['mandi_name'],
        orientation='h',
        marker=dict(color=colors),
        text=top_mandis['total_arrival_qty_qtl'].apply(lambda x: f"{x:,.0f} Qtl"),
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Arrivals: %{x:,.0f} Qtl<br>District: %{customdata[0]}<extra></extra>',
        customdata=top_mandis[['district']]
    ))

    fig.update_layout(
        title=f'Top {top_n} Mandis by Arrival Volume (Top 5 Highlighted in Blue)',
        xaxis_title='Arrival Quantity (Quintals)',
        yaxis_title='',
        template='plotly_white',
        margin=dict(l=150, r=40, t=60, b=40),
        height=400
    )

    return fig

def chart_crop_distribution(crop_kpis_df):
    """Donut chart showing crop arrival distribution"""
    if crop_kpis_df is None or len(crop_kpis_df) == 0:
        return go.Figure()

    fig = px.pie(
        crop_kpis_df,
        values='total_arrivals_qtl',
        names='crop_name',
        hole=0.45,
        title='Arrivals by Canonical Crop (Cleaned Data)',
        color_discrete_sequence=px.colors.qualitative.Prism
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Arrivals: %{value:,.0f} Qtl<br>Share: %{percent}<extra></extra>'
    )

    fig.update_layout(
        template='plotly_white',
        margin=dict(l=40, r=40, t=60, b=40),
        showlegend=False,
        height=350
    )

    return fig

def chart_price_vs_msp(crop_kpis_df):
    """Grouped bar chart comparing Modal Price vs MSP by crop"""
    if crop_kpis_df is None or len(crop_kpis_df) == 0:
        return go.Figure()

    df = crop_kpis_df.sort_values('total_arrivals_qtl', ascending=False)

    fig = go.Figure()

    # Modal Price
    fig.add_trace(go.Bar(
        name='Modal Price',
        x=df['crop_name'],
        y=df['avg_modal_price'],
        marker_color='#3182ce',
        text=df['avg_modal_price'].apply(lambda x: f"Rs. {x:,.0f}"),
        textposition='auto'
    ))

    # MSP
    fig.add_trace(go.Bar(
        name='MSP',
        x=df['crop_name'],
        y=df['avg_msp'],
        marker_color='#dd6b20',
        text=df['avg_msp'].apply(lambda x: f"Rs. {x:,.0f}"),
        textposition='auto'
    ))

    fig.update_layout(
        title='Modal Price vs Minimum Support Price (MSP) by Crop',
        xaxis_title='Crop',
        yaxis_title='Price (Rs. / Quintal)',
        barmode='group',
        template='plotly_white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=400
    )

    return fig

def chart_price_vulnerability_matrix(crop_kpis_df):
    """Scatter plot: Price Vulnerability Matrix (Volume vs Crash Rate)"""
    if crop_kpis_df is None or len(crop_kpis_df) == 0:
        return go.Figure()

    df = crop_kpis_df.copy()

    # Size proportional to farmer count
    df['bubble_size'] = np.sqrt(df['farmer_count'].fillna(100)) * 2

    # Color by crash rate
    fig = px.scatter(
        df,
        x='total_arrivals_qtl',
        y='price_crash_rate',
        size='bubble_size',
        color='price_crash_rate',
        text='crop_name',
        color_continuous_scale='Reds',
        title='Price Vulnerability Matrix (Arrival Volume × Below-MSP Rate)',
        labels={
            'total_arrivals_qtl': 'Total Arrival Volume (Quintals)',
            'price_crash_rate': 'Price Crash Rate (% below MSP)'
        },
        hover_data={
            'crop_name': True,
            'total_arrivals_qtl': ':,.0f',
            'price_crash_rate': ':.1f',
            'price_crash_count': True,
            'bubble_size': False
        }
    )

    # Reference lines for quadrant analysis
    median_vol = df['total_arrivals_qtl'].median()
    fig.add_vline(x=median_vol, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=30, line_dash="dash", line_color="red", opacity=0.7, annotation_text="30% Risk Threshold")

    fig.update_traces(textposition='top center')

    fig.update_layout(
        template='plotly_white',
        margin=dict(l=40, r=40, t=60, b=40),
        height=450
    )

    return fig

def chart_warehouse_transit(warehouse_kpis_df, p90_threshold):
    """Bar chart of median transit time by warehouse with p90 line"""
    if warehouse_kpis_df is None or len(warehouse_kpis_df) == 0:
        return go.Figure()

    df = warehouse_kpis_df.sort_values('median_transit_hours', ascending=False)

    fig = go.Figure()

    # Median transit
    fig.add_trace(go.Bar(
        x=df['destination_warehouse'],
        y=df['median_transit_hours'],
        name='Median Transit',
        marker_color='#4299e1',
        text=df['median_transit_hours'].apply(lambda x: f"{x:.1f}h"),
        textposition='auto'
    ))

    # P90 line
    fig.add_hline(
        y=p90_threshold,
        line_dash="dash",
        line_color="#e53e3e",
        annotation_text=f"Overall P90 Threshold ({p90_threshold:.1f}h)",
        annotation_position="top right"
    )

    fig.update_layout(
        title='Warehouse Transit Duration (Median Hours)',
        xaxis_title='Destination Warehouse',
        yaxis_title='Transit Hours',
        template='plotly_white',
        margin=dict(l=40, r=40, t=60, b=40),
        height=380
    )

    return fig

def chart_weather_arrival_sync(weather_arrival_df):
    """Dual-axis chart: Rainfall vs Total Arrivals across synchronized dates"""
    if weather_arrival_df is None or len(weather_arrival_df) == 0:
        return go.Figure()

    df = weather_arrival_df.sort_values('date')

    fig = go.Figure()

    # Arrivals on left Y
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['total_arrivals_qtl'],
        name='Total Arrivals (Qtl)',
        line=dict(color='#3182ce', width=2),
        yaxis='y1'
    ))

    # Rainfall on right Y
    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['total_rainfall_mm'],
        name='Daily Rainfall (mm)',
        marker_color='rgba(66, 153, 225, 0.3)',
        yaxis='y2'
    ))

    fig.update_layout(
        title='Weather-to-Arrival Synchronization (Date-Level)',
        xaxis_title='Date',
        yaxis=dict(
            title='Arrivals (Quintals)',
            titlefont=dict(color='#3182ce'),
            tickfont=dict(color='#3182ce')
        ),
        yaxis2=dict(
            title='Rainfall (mm)',
            titlefont=dict(color='#63b3ed'),
            tickfont=dict(color='#63b3ed'),
            overlaying='y',
            side='right'
        ),
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=400
    )

    return fig
