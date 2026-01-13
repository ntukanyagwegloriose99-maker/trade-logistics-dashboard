import streamlit as st
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Global Trade & Logistics Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS FOR COLORFUL DESIGN ====================
st.markdown("""
    <style>
    /* Main background gradient */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    
    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin: 10px 0;
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .kpi-label {
        font-size: 1rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Filter labels */
    .stSelectbox label, .stMultiSelect label {
        color: white !important;
        font-weight: bold;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    </style>
""", unsafe_allow_html=True)

# ==================== LOAD DATA ====================
@st.cache_data
def load_data():
    """Load and prepare the dataset"""
    df = pd.read_excel('data/Oc_data.xlsx')
    
    # Calculate average LPI score
    lpi_columns = ['LPI_CUSTOM', 'LPI_INFRA', 'LPI_EASE', 'LPI_QUALITY', 'LPI_TRACK', 'LPI_TIME']
    df['Avg_LPI'] = df[lpi_columns].mean(axis=1)
    
    # Calculate Trade per Capita
    df['Trade_per_Capita'] = df['Total'] / df['Population']
    
    return df

# Load data
try:
    df = load_data()
    st.sidebar.success("✅ Data loaded successfully!")
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# ==================== SIDEBAR - GLOBAL FILTERS ====================
st.sidebar.title("🌍 Global Trade & Logistics")
st.sidebar.markdown("---")

# Year Filter
years = sorted(df['Year'].unique())
selected_year = st.sidebar.selectbox(
    "📅 Select Year",
    options=years,
    index=len(years)-1  # Default to most recent year
)

# Country Filter
countries = ['All'] + sorted(df['Country'].unique().tolist())
selected_country = st.sidebar.multiselect(
    "🌏 Select Country/Countries",
    options=countries,
    default=['All']
)

st.sidebar.markdown("---")
st.sidebar.info("""
📊 **Dashboard Info**
- 7 Oceania Countries
- 6 Time Points (2007-2018)
- 15 Indicators
""")

# ==================== FILTER DATA ====================
def filter_data(df, year, countries):
    """Apply filters to the dataset"""
    filtered = df[df['Year'] == year].copy()
    
    if 'All' not in countries:
        filtered = filtered[filtered['Country'].isin(countries)]
    
    return filtered

filtered_df = filter_data(df, selected_year, selected_country)

# ==================== MAIN HEADER ====================
st.title("🌍 Global Trade & Logistics Analysis Dashboard")
st.markdown(f"### 📊 Analyzing {selected_year} Data for Oceania Region")
st.markdown("---")

# ==================== CREATE TABS FOR PAGES ====================
tab1, tab2, tab3 = st.tabs([
    "📦 Trade Overview", 
    "💰 Economic Context", 
    "🚚 Logistics Performance"
])

# ==================== PAGE 1: TRADE OVERVIEW ====================
with tab1:
    st.header("📦 Trade Overview")
    
    if len(filtered_df) == 0:
        st.warning("⚠️ No data available for selected filters")
    else:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_export = filtered_df['Export'].sum()
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Total Export</div>
                    <div class="kpi-value">${total_export/1e9:.2f}B</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_import = filtered_df['Import'].sum()
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Total Import</div>
                    <div class="kpi-value">${total_import/1e9:.2f}B</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            trade_balance = filtered_df['Trade Balance'].sum()
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Trade Balance</div>
                    <div class="kpi-value">${trade_balance/1e9:.2f}B</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_trade = filtered_df['Total'].sum()
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Total Trade</div>
                    <div class="kpi-value">${total_trade/1e9:.2f}B</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts Row 1: Export & Import Trends
        st.subheader("📈 Export & Import Trends Over Time")
        
        # Get time series data
        if 'All' in selected_country:
            time_df = df.groupby('Year')[['Export', 'Import']].sum().reset_index()
        else:
            time_df = df[df['Country'].isin(selected_country)].groupby('Year')[['Export', 'Import']].sum().reset_index()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=time_df['Year'], 
            y=time_df['Export']/1e9,
            name='Export',
            line=dict(color='#00d2ff', width=3),
            mode='lines+markers'
        ))
        fig_trend.add_trace(go.Scatter(
            x=time_df['Year'], 
            y=time_df['Import']/1e9,
            name='Import',
            line=dict(color='#f093fb', width=3),
            mode='lines+markers'
        ))
        fig_trend.update_layout(
            title="Export & Import vs Year (Billions USD)",
            xaxis_title="Year",
            yaxis_title="Value (Billions USD)",
            template="plotly_dark",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Charts Row 2: Trade by Country and Trade Balance
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌏 Total Trade by Country")
            fig_country = px.bar(
                filtered_df.sort_values('Total', ascending=True),
                y='Country',
                x='Total',
                orientation='h',
                title=f"Total Trade by Country ({selected_year})",
                labels={'Total': 'Total Trade (USD)', 'Country': ''},
                color='Total',
                color_continuous_scale='Viridis'
            )
            fig_country.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_country, use_container_width=True)
        
        with col2:
            st.subheader("⚖️ Trade Balance by Country")
            fig_balance = px.bar(
                filtered_df.sort_values('Trade Balance'),
                y='Country',
                x='Trade Balance',
                orientation='h',
                title=f"Trade Balance by Country ({selected_year})",
                labels={'Trade Balance': 'Trade Balance (USD)', 'Country': ''},
                color='Trade Balance',
                color_continuous_scale='RdYlGn'
            )
            fig_balance.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_balance, use_container_width=True)

# ==================== PAGE 2: ECONOMIC CONTEXT ====================
with tab2:
    st.header("💰 Economic Context")
    
    if len(filtered_df) == 0:
        st.warning("⚠️ No data available for selected filters")
    else:
        # KPIs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_gdp = filtered_df['GDP'].sum()
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Total GDP</div>
                    <div class="kpi-value">${total_gdp/1e9:.2f}B</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_pop = filtered_df['Population'].sum()
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Total Population</div>
                    <div class="kpi-value">{total_pop/1e6:.2f}M</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_trade_per_capita = (filtered_df['Total'].sum() / filtered_df['Population'].sum())
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Avg Trade per Capita</div>
                    <div class="kpi-value">${avg_trade_per_capita:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts Row 1: GDP vs Trade
        st.subheader("📊 GDP vs Total Trade")
        fig_gdp_trade = px.scatter(
            filtered_df,
            x='GDP',
            y='Total',
            size='Population',
            color='Country',
            hover_name='Country',
            title=f"GDP vs Total Trade ({selected_year})",
            labels={'GDP': 'GDP (USD)', 'Total': 'Total Trade (USD)'},
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        fig_gdp_trade.update_layout(template="plotly_dark", height=500)
        st.plotly_chart(fig_gdp_trade, use_container_width=True)
        
        # Charts Row 2: Population vs Trade and Trade per Capita
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Population vs Trade")
            fig_pop_trade = px.scatter(
                filtered_df,
                x='Population',
                y='Total',
                size='GDP',
                color='Country',
                hover_name='Country',
                title=f"Population vs Trade ({selected_year})",
                labels={'Population': 'Population', 'Total': 'Total Trade (USD)'},
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_pop_trade.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_pop_trade, use_container_width=True)
        
        with col2:
            st.subheader("💵 Trade per Capita by Country")
            fig_per_capita = px.bar(
                filtered_df.sort_values('Trade_per_Capita', ascending=True),
                y='Country',
                x='Trade_per_Capita',
                orientation='h',
                title=f"Trade per Capita ({selected_year})",
                labels={'Trade_per_Capita': 'Trade per Capita (USD)', 'Country': ''},
                color='Trade_per_Capita',
                color_continuous_scale='Plasma'
            )
            fig_per_capita.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_per_capita, use_container_width=True)

# ==================== PAGE 3: LOGISTICS PERFORMANCE ====================
with tab3:
    st.header("🚚 Logistics Performance & Trade Efficiency")
    
    if len(filtered_df) == 0:
        st.warning("⚠️ No data available for selected filters")
    else:
        # KPI
        avg_lpi = filtered_df['Avg_LPI'].mean()
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Average LPI Score</div>
                    <div class="kpi-value">{avg_lpi:.2f}</div>
                    <div class="kpi-label">Out of 5.0</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts Row 1: LPI Indicators Comparison (Radar Chart)
        st.subheader("📡 LPI Indicators Comparison")
        
        lpi_cols = ['LPI_CUSTOM', 'LPI_INFRA', 'LPI_EASE', 'LPI_QUALITY', 'LPI_TRACK', 'LPI_TIME']
        lpi_labels = ['Customs', 'Infrastructure', 'Ease of Shipment', 'Service Quality', 'Tracking', 'Timeliness']
        
        # Create radar chart for each country
        fig_radar = go.Figure()
        
        for _, row in filtered_df.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[row[col] for col in lpi_cols],
                theta=lpi_labels,
                fill='toself',
                name=row['Country']
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5])
            ),
            showlegend=True,
            title=f"LPI Indicators by Country ({selected_year})",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Charts Row 2: LPI vs Export and LPI by Country
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Average LPI vs Export Value")
            fig_lpi_export = px.scatter(
                filtered_df,
                x='Avg_LPI',
                y='Export',
                size='GDP',
                color='Country',
                hover_name='Country',
                title=f"LPI Score vs Export ({selected_year})",
                labels={'Avg_LPI': 'Average LPI Score', 'Export': 'Export Value (USD)'},
                color_discrete_sequence=px.colors.qualitative.Set2,
                trendline="ols"
            )
            fig_lpi_export.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_lpi_export, use_container_width=True)
        
        with col2:
            st.subheader("🏆 Average LPI by Country")
            fig_lpi_country = px.bar(
                filtered_df.sort_values('Avg_LPI', ascending=True),
                y='Country',
                x='Avg_LPI',
                orientation='h',
                title=f"Average LPI Score by Country ({selected_year})",
                labels={'Avg_LPI': 'Average LPI Score', 'Country': ''},
                color='Avg_LPI',
                color_continuous_scale='Turbo'
            )
            fig_lpi_country.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_lpi_country, use_container_width=True)
        
        # LPI Components Breakdown
        st.subheader("📊 Detailed LPI Components")
        lpi_breakdown = filtered_df[['Country'] + lpi_cols].set_index('Country')
        lpi_breakdown.columns = lpi_labels
        
        fig_components = px.bar(
            lpi_breakdown.reset_index().melt(id_vars='Country', var_name='Indicator', value_name='Score'),
            x='Country',
            y='Score',
            color='Indicator',
            barmode='group',
            title=f"LPI Components Breakdown ({selected_year})",
            labels={'Score': 'LPI Score', 'Country': '', 'Indicator': 'LPI Indicator'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_components.update_layout(template="plotly_dark", height=500)
        st.plotly_chart(fig_components, use_container_width=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: white;'>
        <p>🌍 Global Trade & Logistics Analysis Dashboard | Built with Streamlit & Plotly</p>
        <p>📊 Data Source: Oceania Trade & Logistics Dataset (2007-2018)</p>
    </div>
""", unsafe_allow_html=True) 
