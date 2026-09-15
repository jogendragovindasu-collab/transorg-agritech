# Theme colors for dark navy dashboard with light analytical chart surfaces
THEME = {
    'bg_dark': '#0B1420',
    'bg_card': '#142231',
    'bg_card_light': '#FFFFFF',
    'text_primary': '#172033',
    'text_secondary': '#526070',
    'text_muted': '#8A98AB',
    'emerald': '#22C98A',
    'warning': '#F5B84B',
    'danger': '#F45B69',
    'blue': '#5B8DEF',
    'border': '#E5EAF0',
    'border_dark': '#26384A',
    'grid_light': '#E5EAF0',
}

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
        line=dict(color=THEME['emerald'], width=2),
        opacity=0.9
    ))

    # 7-day moving average
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['rolling_7d'],
        mode='lines',
        name='7-Day Trend',
        line=dict(color=THEME['warning'], width=3)
    ))

    fig.update_layout(
        title='Daily Arrival Volume (Quintals)',
        title_font=dict(color='#172033', size=16, family='Inter'),
        xaxis_title='Date',
        xaxis_title_font=dict(color='#526070'),
        yaxis_title='Arrivals (Qtl)',
        yaxis_title_font=dict(color='#526070'),
        font=dict(family='Inter', color='#172033'),
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        hovermode='x unified',
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
            font=dict(color='#172033'), bgcolor='#FFFFFF', bordercolor='#26384A',
            borderwidth=1
        ),
        margin=dict(l=50, r=40, t=70, b=50),
        height=420,
        xaxis=dict(
            gridcolor='#E5EAF0', zerolinecolor='#E5EAF0',
            tickfont=dict(color='#526070'),
            showline=True, linecolor='#D1D5DB', linewidth=1
        ),
        yaxis=dict(
            gridcolor='#E5EAF0', zerolinecolor='#E5EAF0',
            tickfont=dict(color='#526070'),
            showline=True, linecolor='#D1D5DB', linewidth=1
        )
    )
    return fig

def chart_supply_concentration(mandi_kpis_df, top_n=10):
    """Horizontal bar chart for top mandis by arrival volume"""
    if mandi_kpis_df is None or len(mandi_kpis_df) == 0:
        return go.Figure()

    top_mandis = mandi_kpis_df.nlargest(top_n, 'total_arrival_qty_qtl').sort_values('total_arrival_qty_qtl')

    colors = [THEME['blue'] if i >= (top_n - 5) else THEME['text_muted'] for i in range(len(top_mandis))]

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
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(family='Inter', color='#172033'),
        title_font=dict(color='#172033', size=14),
        margin=dict(l=150, r=40, t=60, b=40),
        height=400,
        xaxis=dict(
            gridcolor='#E5EAF0', zerolinecolor='#E5EAF0', tickfont=dict(color='#526070'),
            showline=True, linecolor='#D1D5DB', linewidth=1
        ),
        yaxis=dict(
            gridcolor='#E5EAF0', zerolinecolor='#E5EAF0', tickfont=dict(color='#172033'),
            showline=True, linecolor='#D1D5DB', linewidth=1
        )
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
        title='Arrivals by Canonical Crop (Cleaned Data)',
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(family='Inter', color='#172033'),
        title_font=dict(color='#172033', size=14),
        legend=dict(bgcolor='#FFFFFF', bordercolor='#26384A', font=dict(color='#172033'), borderwidth=1),
        margin=dict(l=40, r=40, t=60, b=40),
        showlegend=True,
        height=350,
        xaxis=dict(gridcolor='#E5EAF0', tickfont=dict(color='#526070'), showline=True, linecolor='#D1D5DB'),
        yaxis=dict(gridcolor='#E5EAF0', tickfont=dict(color='#526070'), showline=True, linecolor='#D1D5DB')
    )
    return fig

def chart_price_vs_msp(crop_kpis_df):
    """Grouped bar chart comparing Modal Price vs MSP by crop"""
    if crop_kpis_df is None or len(crop_kpis_df) == 0:
        return go.Figure()

    df = crop_kpis_df.sort_values('total_arrivals_qtl', ascending=False)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Modal Price',
        x=df['crop_name'],
        y=df['avg_modal_price'],
        marker_color=THEME['blue'],
        text=df['avg_modal_price'].apply(lambda x: f"Rs. {x:,.0f}"),
        textposition='auto'
    ))

    fig.add_trace(go.Bar(
        name='MSP',
        x=df['crop_name'],
        y=df['avg_msp'],
        marker_color=THEME['emerald'],
        text=df['avg_msp'].apply(lambda x: f"Rs. {x:,.0f}"),
        textposition='auto'
    ))

    fig.update_layout(
        title='Modal Price vs Minimum Support Price (MSP) by Crop',
        xaxis_title='Crop',
        yaxis_title='Price (Rs. / Quintal)',
        barmode='group',
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(family='Inter', color='#172033'),
        title_font=dict(color='#172033', size=14),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                    font=dict(color='#172033'), bgcolor='#FFFFFF', bordercolor='#26384A', borderwidth=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=400,
        xaxis=dict(gridcolor='#E5EAF0', zerolinecolor='#E5EAF0', tickfont=dict(color='#526070'), showline=True, linecolor='#D1D5DB'),
        yaxis=dict(gridcolor='#E5EAF0', zerolinecolor='#E5EAF0', tickfont=dict(color='#526070'), showline=True, linecolor='#D1D5DB')
    )
    return fig

def chart_price_vulnerability_matrix(crop_kpis_df):
    """Scatter plot: Price Vulnerability Matrix (Volume vs Crash Rate)"""
    if crop_kpis_df is None or len(crop_kpis_df) == 0:
        return go.Figure()

    df = crop_kpis_df.copy()

    df['bubble_size'] = np.sqrt(df['farmer_count'].fillna(100)) * 2

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

    median_vol = df['total_arrivals_qtl'].median()
    fig.add_vline(x=median_vol, line_dash="dash", line_color="#526070", opacity=0.5)
    fig.add_hline(y=30, line_dash="dash", line_color="#F45B69", opacity=0.7, annotation_text="30% Risk Threshold", annotation_font=dict(color="#172033"))

    fig.update_traces(textposition='top center', textfont=dict(color='#172033'))

    fig.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(family='Inter', color='#172033'),
        title_font=dict(color='#172033', size=14),
        legend=dict(bgcolor='#FFFFFF', bordercolor='#26384A', font=dict(color='#172033'), borderwidth=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=450,
        xaxis=dict(gridcolor='#E5EAF0', zerolinecolor='#E5EAF0', tickfont=dict(color='#526070'), showline=True, linecolor='#D1D5DB'),
        yaxis=dict(gridcolor='#E5EAF0', zerolinecolor='#E5EAF0', tickfont=dict(color='#526070'), showline=True, linecolor='#D1D5DB')
    )
    return fig

def chart_warehouse_transit(warehouse_kpis_df, p90_threshold):
    """Bar chart of median transit time by warehouse with p90 line"""
    if warehouse_kpis_df is None or len(warehouse_kpis_df) == 0:
        return go.Figure()

    df = warehouse_kpis_df.sort_values('median_transit_hours', ascending=False)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['destination_warehouse'],
        y=df['median_transit_hours'],
        name='Median Transit',
        marker_color='#5B8DEF',
        text=df['median_transit_hours'].apply(lambda x: f"{x:.1f}h"),
        textposition='auto'
    ))

    fig.add_hline(
        y=p90_threshold,
        line_dash="dash",
        line_color="#F45B69",
        annotation_text=f"Overall P90 Threshold ({p90_threshold:.1f}h)",
        annotation_position="top right",
        annotation_font=dict(color='#172033')
    )

    fig.update_layout(
        title='Warehouse Transit Duration (Median Hours)',
        xaxis_title='Destination Warehouse',
        yaxis_title='Transit Hours',
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(family='Inter', color='#172033'),
        title_font=dict(color='#172033', size=14),
        legend=dict(bgcolor='#FFFFFF', bordercolor='#26384A', font=dict(color='#172033'), borderwidth=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=380,
        xaxis=dict(gridcolor='#E5EAF0', zerolinecolor='#E5EAF0', tickfont=dict(color='#526070'), showline=True, linecolor='#D1D5DB'),
        yaxis=dict(gridcolor='#E5EAF0', zerolinecolor='#E5EAF0', tickfont=dict(color='#526070'), showline=True, linecolor='#D1D5DB')
    )
    return fig

def chart_weather_arrival_sync(weather_arrival_df):
    """Dual-axis chart: Rainfall vs Total Arrivals across synchronized dates"""
    if weather_arrival_df is None or len(weather_arrival_df) == 0:
        return go.Figure()

    df = weather_arrival_df.sort_values('date')

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['total_arrivals_qtl'],
        name='Total Arrivals (Qtl)',
        line=dict(color='#5B8DEF', width=2),
        yaxis='y1'
    ))

    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['total_rainfall_mm'],
        name='Daily Rainfall (mm)',
        marker_color='rgba(66, 153, 225, 0.5)',
        yaxis='y2'
    ))

    fig.update_layout(
        title='Weather-to-Arrival Synchronization (Date-Level)',
        xaxis_title='Date',
        yaxis=dict(
            title='Arrivals (Quintals)',
            titlefont=dict(color='#5B8DEF'),
            tickfont=dict(color='#526070'),
            gridcolor='#E5EAF0', zerolinecolor='#E5EAF0',
            showline=True, linecolor='#D1D5DB'
        ),
        yaxis2=dict(
            title='Rainfall (mm)',
            titlefont=dict(color='#3182CE'),
            tickfont=dict(color='#526070'),
            overlaying='y',
            side='right',
            gridcolor='#E5EAF0', zerolinecolor='#E5EAF0',
            showline=True, linecolor='#D1D5DB'
        ),
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                    font=dict(color='#172033'), bgcolor='#FFFFFF', bordercolor='#26384A', borderwidth=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=400,
        font=dict(family='Inter', color='#172033'),
        title_font=dict(color='#172033', size=14)
    )
    return fig
