# DASHBOARD LAYOUT
# Streamlit
import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Live Data
from live.live_data_analysis import build_live_processed_df
# Import Libraries
import streamlit as st

import plotly.express as px
import pandas as pd
# Load files to integrate
from stats.risk_summary import(
    takeoff_risk_distribution,
    landing_risk_distribution,
    enroute_risk_distribution
)
from modules.module_2 import render_module2

import base64

def get_base64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img = get_base64("ui/pilot.jpeg")

# Load Dastasets once
data_files={
    "JFK":"data/processed/jfk_risk_output.csv",
    "Madrid":"data/processed/madrid_risk_output.csv"
}
dfs={airport:pd.read_csv(path) for airport, path in data_files.items()}

AIRPORT_ICAO_MAP = {
    "JFK": "KJFK",
    "London Heathrow": "EGLL",
    "Dubai": "OMDB",
    "Mumbai": "VABB",
    "Delhi": "VIDP",
    "Madrid": "LEMD",
    "Singapore": "WSSS"
}

def render_dashboard():
    
    # ---------- SIDEBAR ----------
    with st.sidebar:
        # Access the mode selected in app.py
        data_mode = st.session_state.main_data_mode

        if data_mode=="Live Data":
            live_window = st.selectbox(
                "🕒Live Time Window",              # Label
                ["Last 60 min","Last 120 min", "Last 130 min","Last 140 min", "Last 150 min","Last 160 min"], # Options
                key="live_window"                # Optional key
            )
        st.markdown("<hr>", unsafe_allow_html=True)
        
    with st.container():
        # ---------- TOP BAR ----------
        # Deafult top bar values
        selected_airport=(st.session_state.selected_airport if "selected_airport" in st.session_state else "JFK")
        selected_phase=(st.session_state.selected_phase if "selected_phase" in st.session_state else "ENROUTE")

        st.markdown(f"""
            <div class="topbar">
                <h2>{selected_phase} ANALYTICS {selected_airport}</h2>  
                <div class="profile">
                <span>Hello, ATC 👋</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    

         # ---------- FILTER CARDS ----------
        fcol,col1, col2, col3 = st.columns(4)
        # Filter data
        HISTORICAL_AIRPORTS = ["JFK", "Madrid"] 
        with fcol:
            # Open the card container
            st.markdown("""<div class="card"><div class="class-content"><h4>Select Options</h4>""", unsafe_allow_html=True)
            # Render Dropdown 1
            if data_mode == "Historical Data":
                selected_airport = st.selectbox(
                "Select Airport",
                HISTORICAL_AIRPORTS,   # historical dataset airports
                key="selected_airport"
            )

            else:  # Live Data
                selected_airport = st.selectbox(
                "🛫Select Airport",
                list(AIRPORT_ICAO_MAP.keys()),     # ICAO-mapped airports
                key="selected_airport"
            )
            # Render Dropdown 2
            selected_phase = st.selectbox(
            "🛬Select Phase",
            ["Takeoff", "Landing", "Enroute"],
            key="selected_phase"
            )
    
            # CLOSE the card container
            st.markdown("""</div> </div>""", unsafe_allow_html=True)

        # ------DATA SELECTION (LIVE OR HISTORICAL)------

        # Use selected_airport and selected_phase from dropdown

        if data_mode == "Live Data":
            icao = AIRPORT_ICAO_MAP[selected_airport]


            # Convert dropdown string to minutes
            LIVE_WINDOW_MAP = {
            "Last 60 min": 60,
            "Last 120 min": 120,
            "Last 130 min": 130,
            "Last 140 min": 140,
            "Last 150 min": 150,
            "Last 160 min":160
            }
            minutes = LIVE_WINDOW_MAP.get(st.session_state.live_window, 60)  # default 5 min

            df=build_live_processed_df(
                icao=icao,
                airport_name=selected_airport,
                minutes=minutes
            )
            if df.empty:
                df=pd.DataFrame([
                    {
                        "takeoff_risk":"LOW RISK",
                        "landing_risk":"LOW RISK",
                        "enroute_risk":"ENROUTE SAFE"
                    }
                ])

            # Determine risk column dynamically
            risk_col = {
            "Takeoff": "takeoff_risk",
            "Landing": "landing_risk",
            "Enroute": "enroute_risk"
            }[selected_phase]

            # Live METAR may not have risk columns yet
            if risk_col not in df.columns:
                df[risk_col] = "LOW RISK" if selected_phase != "Enroute" else "ENROUTE SAFE"
            
            df[risk_col]=df[risk_col].astype(str)
            risk_series = df[risk_col]
            total_flights = len(df)

            if selected_phase == "Enroute":
                high_label = "ENROUTE CRITICAL"
                moderate_label = "ENROUTE CAUTION"
                low_label = "ENROUTE SAFE"
            else:
                high_label = "HIGH RISK"
                moderate_label = "MODERATE RISK"
                low_label = "LOW RISK"

        else:
            # Historical Data
            df = dfs[selected_airport]
            risk_col = {
            "Takeoff": "takeoff_risk",
            "Landing": "landing_risk",
            "Enroute": "enroute_risk"
            }[selected_phase]
            # Make sure the column exists, else create default values
            if risk_col not in df.columns or df[risk_col].isnull().all():
                default_value = "ENROUTE SAFE" if selected_phase=="Enroute" else "LOW RISK"
                df[risk_col] = [default_value]*len(df)
            risk_series = df[risk_col]
            total_flights = len(df)

            # Risk Labels
            if selected_phase == "Enroute":
                high_label = "ENROUTE CRITICAL"
                moderate_label = "ENROUTE CAUTION"
                low_label = "ENROUTE SAFE"
            else:
                high_label = "HIGH RISK"
                moderate_label = "MODERATE RISK"
                low_label = "LOW RISK"
        

        # Compute percentages safely
        high_risk_pct = round((risk_series == high_label).mean() * 100, 1)
        moderate_risk_pct = round((risk_series == moderate_label).mean() * 100, 1)
        low_risk_pct = round((risk_series == low_label).mean() * 100, 1)
        
        # Overall Safety Logic
        if selected_phase=="Enroute":
            # For enroute, use stricter thresholds
            if high_risk_pct > 30:
                overall_safety="UNSAFE"
            elif high_risk_pct > 15:
                overall_safety="MODERATE"
            else:
             overall_safety="SAFE"
        else:
            # Takeoff/Landing
            if high_risk_pct > 30:
                overall_safety="UNSAFE"
            elif high_risk_pct > 15:
                overall_safety="MODERATE"
            else:
                overall_safety="SAFE"

        # Computation for Airport Comparison (consider only high risk)
        if selected_phase=="Enroute":
            high_label="ENROUTE CRITICAL"
        else:
            high_label="HIGH RISK"
    
        # Card 1: Total Flights
        if data_mode=="Live Data":
            flights_label="Latest Observations"
        else:
            flights_label="Flights Analyzed"
        with col1:
            st.markdown(f"""
            <div class="card blue">
                <h4>Total Flights Analyzed</h4>
                <h1>✈️{total_flights}</h1>
            </div>
            """, unsafe_allow_html=True)
        # Card 2: High risk
        with col2:
            st.markdown(f"""
            <div class="card orange">
                <h4>High Risk Enroute {selected_phase} %</h4>
                <h1>⚠️{high_risk_pct}</h1>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="card green">
                <h4>Overall Operational Safety</h4>
                <h1>🛡️{overall_safety}</h1>
            </div>
            """, unsafe_allow_html=True)

        # ---------- CHART SECTION ----------
        left, right = st.columns([3,2])

        # Risk Distribution
        # For Live
        if data_mode == "Live Data":
            # Make sure all risk levels appear even if count is 0
            if selected_phase == "Enroute":
                risk_levels = ["ENROUTE CRITICAL", "ENROUTE CAUTION", "ENROUTE SAFE"]
            else:
                risk_levels = ["HIGH RISK", "MODERATE RISK", "LOW RISK"]

            risk_counts = df[risk_col].value_counts().reindex(risk_levels, fill_value=0)
            risk_df = risk_counts.reset_index()
            risk_df.columns = ["Risk Level", "Flights"]

        # For Historical
        else:
            risk_counts=risk_series.value_counts()
            risk_df=risk_counts.reset_index()
            risk_df.columns=["Risk Level","Flights"]
                  
        fig = px.bar(
            risk_df,
            x="Risk Level",
            y="Flights",
            color="Risk Level",
            height=650,
            color_discrete_map={
                "LOW RISK": "#4CAF50",
                "MODERATE RISK": "#FF9800",
                "HIGH RISK": "#F44336",
                "ENROUTE CRITICAL": "#4CAF50",
                "ENROUTE CAUTION": "#FF9800",
                "ENROUTE SAFE": "#F44336"
            }
        )
        with left:
            with st.container(border=True):
                st.markdown("📊Risk Level Chart")
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("""</div></div>""", unsafe_allow_html=True)

        # Airport Comparison (Only for historical data)

        if data_mode=="Historical Data":
            comp = pd.DataFrame({
            "Airport": ["JFK", "Madrid"],
            "High Risk %": [
                round((dfs["JFK"][risk_col]==high_label).mean()*100,1),
                round((dfs["Madrid"][risk_col]==high_label).mean()*100,1)
            ]
            })
            # header
            fig2 = px.bar(
            comp,
            x="Airport",
            y="High Risk %",
            color="Airport",
            height=400,
            text="High Risk %",
            title=f"{selected_phase} High Risk Comparison"
            )

            with right:
                with st.container(border=True):
                    st.markdown("📊Airport Comparison")
                    st.plotly_chart(fig2, use_container_width=True)
                    st.markdown("""</div></div>""", unsafe_allow_html=True)

        # ---------- SUMMARY ----------
        if data_mode == "Live Data":
            right.markdown(f"""
            <div class="card">
            <div class="card-content">
            <h3>Live Snapshot Summary</h3>
            <p>
            {total_flights} flights observed for <strong>{selected_airport}</strong> in the last <strong>{minutes} minutes</strong>.<br>
            High Risk: <strong>{high_risk_pct}%</strong><br>
            Moderate Risk: <strong>{moderate_risk_pct}%</strong><br>
            Low Risk: <strong>{low_risk_pct}%</strong>
            </p>
            </div></div>
            """, unsafe_allow_html=True)
        else:
            right.markdown(f"""
            <div class="card">
            <div class="card-content">
            <h3>Summary</h3>
            <p>
            Enroute operations for <strong>{selected_airport}</strong> during the 
            <strong>{selected_phase}</strong> phase show a <strong>{overall_safety}</strong>
            operational safety level.
            Most flights are low or moderate risk, with <strong>{high_risk_pct}%</strong> high risk flights.
            </p>
            </div></div>
            """, unsafe_allow_html=True)
        