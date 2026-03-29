import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

# Specialized Bundle Imports
from utils.odds_api import OddsAPI
from analytics.models import SportsPredictor
from analytics.ledger import BettingLedger
from analytics.financial_engine import FinancialEngine
from data_fetchers.news_client import NewsIntelligence

load_dotenv()

# --- Page Config & Theme ---
st.set_page_config(
    page_title="BEST BETS | Specialist Terminal",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Specialist Stealth Wealth Styles ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=JetBrains+Mono&display=swap');
    
    * { font-family: 'Outfit', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #020617 0%, #0f172a 50%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    .glass-card {
        background: rgba(148, 163, 184, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .status-pill {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .pill-safe { background: rgba(34, 197, 94, 0.1); color: #4ade80; border: 1px solid #22c55e; }
    .pill-value { background: rgba(234, 179, 8, 0.1); color: #facc15; border: 1px solid #eab308; }
    .pill-upset { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid #ef4444; }

    .metric-mono { font-family: 'JetBrains Mono', monospace; color: #38bdf8; }
    
    /* GSAP Pulse Animation Simulation */
    @keyframes pulse-glow {
        0% { box-shadow: 0 0 5px rgba(56, 189, 248, 0.2); }
        50% { box-shadow: 0 0 20px rgba(56, 189, 248, 0.6); }
        100% { box-shadow: 0 0 5px rgba(56, 189, 248, 0.2); }
    }
    .active-alert { border: 1px solid #38bdf8 !important; animation: pulse-glow 2s infinite; }
</style>
""", unsafe_allow_html=True)

# --- Initialization ---
@st.cache_resource
def init_engine():
    return {
        "predictor": SportsPredictor(),
        "api": OddsAPI(),
        "ledger": BettingLedger(),
        "fin_engine": FinancialEngine(),
        "intel": NewsIntelligence()
    }

engine = init_engine()

# --- Sidebar Command Center ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/financial-growth-analysis.png", width=80)
    st.title("COMMAND CENTER")
    
    st.markdown("### 🏦 Capital Management")
    initial_equity = st.slider("Initial Principal ($)", 100, 50000, 10000, step=100)
    kelly_fraction = st.select_slider("Staking Aggression (Kelly)", options=[0.1, 0.25, 0.5, 1.0], value=0.25)
    
    st.markdown("---")
    st.markdown("### 🏟️ Market Selection")
    selected_sport = st.selectbox("Sport", ["NBA", "NFL", "MLB", "NHL"], index=0)
    region = st.selectbox("Region", ["us", "uk", "eu", "au"], index=0)
    
    if st.button("🔄 Sync Live Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- Main Dashboard Tabs ---
tab_predictor, tab_portfolio, tab_bestbets, tab_intel = st.tabs([
    "🎯 Predictor Terminal", 
    "💰 Portfolio & Ledger", 
    "🏆 Value Scanner", 
    "📰 Intelligence Hub"
])

SPORT_KEY_MAP = {
    "NBA": "basketball_nba",
    "NFL": "americanfootball_nfl",
    "MLB": "baseball_mlb",
    "NHL": "icehockey_nhl"
}

# --- Shared Logic: Fetch News & Injuries for Catalysts ---
injuries = engine["intel"].get_injury_reports(selected_sport)
catalysts = {i['team']: 0.95 for i in injuries if i['status'] == "Out"} # Simple impact weighting

# --- TAB 1: PREDICTOR TERMINAL ---
with tab_predictor:
    st.title("🎯 Quantitative Predictor")
    st.markdown("Real-time win probabilities driven by Catalyst-Weighted Poisson models.")
    
    odds_data = engine["api"].get_odds(sport=SPORT_KEY_MAP[selected_sport], regions=region)
    df_odds = engine["api"].parse_odds(odds_data)
    
    if not df_odds.empty:
        df_games = df_odds.groupby('id').first().reset_index()
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("### 📊 Market Discrepancy Map")
            fig = px.scatter(df_games, x='home_price', y='away_price', 
                             hover_name='home_team', text='home_team',
                             title="Odds Clustering & Value Identification",
                             template="plotly_dark", color_discrete_sequence=['#38bdf8'])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown("### 🧠 AI Simulation Logic")
            st.markdown(f"""
            <div class="glass-card">
                <p><b>Model</b>: Poisson-Bayesian v4.2</p>
                <p><b>Simulations</b>: 100,000 runs per game</p>
                <p><b>Catalysts</b>: {len(injuries)} active reports</p>
                <hr>
                <p style='color: #94a3b8; font-size: 0.85rem;'>The model currently favors home field advantage and adjusts team λ based on roster integrity.</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Raw Data Table
        st.markdown("### 📝 Raw Market Feed")
        st.dataframe(df_games[['home_team', 'away_team', 'home_price', 'away_price']], use_container_width=True)
    else:
        st.warning("Awaiting market data synchronization...")

# --- TAB 2: PORTFOLIO & LEDGER ---
with tab_portfolio:
    st.title("💰 Capital Allocation & Performance")
    
    perf = engine["ledger"].calculate_performance()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Equity", f"${initial_equity + perf.get('total_profit', 0):,.2f}")
    m2.metric("Portfolio ROI", f"{perf.get('roi', 0):.1%}")
    m3.metric("Sharpe Ratio", f"{perf.get('sharpe', 0):.2f}")
    m4.metric("Max Drawdown", f"${perf.get('max_drawdown', 0):,.2f}")
    
    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("### 📈 Equity Curve")
        if not engine["ledger"].ledger.empty:
            fig = px.line(engine["ledger"].ledger, x='date', y='equity', title="Portfolio Growth Audit", template="plotly_dark")
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No recorded transactions in the current ledger period.")
            
    with c2:
        st.markdown("### 📒 General Ledger")
        st.dataframe(engine["ledger"].ledger[["date", "team", "stake", "profit", "status"]], height=300)

# --- TAB 3: VALUE SCANNER (BEST BETS) ---
with tab_bestbets:
    st.title("🏆 High-Yield Value Scanner")
    st.markdown("Risk-graded opportunities with Fractional Kelly staking suggestions.")
    
    if not df_odds.empty:
        col_low, col_med, col_high = st.columns(3)
        
        with col_low:
            st.markdown("#### 🔒 LOW RISK (Safe Locks)")
        with col_med:
            st.markdown("#### ⚖️ MED RISK (Value Plays)")
        with col_high:
            st.markdown("#### 🔥 HIGH RISK (Upset Alerts)")

        for _, row in df_games.iterrows():
            analysis = engine["predictor"].analyze_bet(row['home_team'], row['away_team'], row['home_price'], row['away_price'], catalysts=catalysts)
            
            for side in ['home', 'away']:
                res = analysis[side]
                risk = engine["fin_engine"].assess_risk_level(res['prob'], res['edge'])
                stake_pct = engine["fin_engine"].calculate_fractional_kelly(res['prob'], row[f'{side}_price'], fraction=kelly_fraction)
                
                if risk == "Not Recommended": continue
                
                target_col = col_low if "Low" in risk else col_med if "Med" in risk else col_high
                pill_class = "pill-safe" if "Low" in risk else "pill-value" if "Med" in risk else "pill-upset"
                card_class = "active-alert" if stake_pct > 0.05 else ""
                
                with target_col:
                    st.markdown(f"""
                    <div class="glass-card {card_class}">
                        <span class="status-pill {pill_class}">{risk}</span>
                        <h4 style="margin: 10px 0;">{res['team']}</h4>
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <p style="color: #94a3b8; font-size: 0.8rem;">PROBABILITY</p>
                                <p class="metric-mono">{res['prob']:.1%}</p>
                            </div>
                            <div>
                                <p style="color: #94a3b8; font-size: 0.8rem;">EDGE</p>
                                <p class="metric-mono">{res['edge']:.1%}</p>
                            </div>
                        </div>
                        <hr style="border-color: rgba(255,255,255,0.05);">
                        <p style="color: #94a3b8; font-size: 0.8rem;">RECOMMENDED STAKE</p>
                        <p style="font-size: 1.2rem; font-weight: 600; color: #4ade80;">${initial_equity * stake_pct:,.2f} <span style="font-size: 0.8rem; font-weight: normal; color: #94a3b8;">({stake_pct:.1%})</span></p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Sync live market data to identify active opportunities.")

# --- TAB 4: INTELLIGENCE HUB ---
with tab_intel:
    st.title("📰 Real-time Intelligence Hub")
    
    col_news, col_injuries = st.columns([2, 1])
    
    with col_news:
        st.markdown("### 📡 Global Sports Feed")
        articles = engine["intel"].get_headlines(selected_sport)
        for art in articles[:10]:
            st.markdown(f"""
            <div class="glass-card">
                <small style="color: #94a3b8;">{art['publishedAt'][:10]}</small>
                <h5 style="margin: 5px 0;">{art['title']}</h5>
                <p style="font-size: 0.9rem; color: #cbd5e1;">{art['description']}</p>
                <a href="{art['url']}" target="_blank" style="color: #38bdf8; text-decoration: none; font-size: 0.8rem;">Read Full Report →</a>
            </div>
            """, unsafe_allow_html=True)
            
    with col_injuries:
        st.markdown("### 🏥 Injury Tracker")
        for inj in injuries:
            st.markdown(f"""
            <div class="glass-card">
                <strong>{inj['player']}</strong> ({inj['team']})
                <br><span style="color: #ef4444;">{inj['status']}</span> - {inj['reason']}
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #888;'>Powered by BEST BETS Specialist Engine | v2.0 Ultimate Edition</p>", unsafe_allow_html=True)
