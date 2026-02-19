import streamlit as st
import pandas as pd
from modules.dashboard import render_dashboard
from modules.module_2 import render_module2
from modules.module_3 import render_module3
from modules.module_4 import render_module4
from atc_auth.atc_login import create_user,login

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ----------------------
# LOGIN / SIGNUP
# ----------------------
if not st.session_state.logged_in:

    option = st.selectbox("Select", ["Login", "Sign Up"])

    st.markdown("""
*Username format:* FIRST 5 LETTERS OF NAME @AIR_1234  
Example: RICHA@BOM_2025

*Password format:* 5 letter (camel case) + 1 special charc + combo of 4 number s 
Example: Richa@8659
""")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Sign Up":
        if st.button("Create"):
            success, msg = create_user(username, password)
            if success:
                st.success(msg)
            else:
                st.error(msg)

    else:
        if st.button("Login"):
            if login(username, password):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")

    st.stop()   # ⬅️ VERY IMPORTANT

# ---------- PAGE CONFIG ----------
st.set_page_config(
page_title="SkyGen AI",
page_icon="✈️",
layout="wide",
initial_sidebar_state="expanded"
)

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="SkyGen AI", page_icon="✈️", layout="wide")

# ---------- LOAD CSS ----------
def load_css():
    with open("ui/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#----------- SIDEBAR (Global Navigation) -----------
with st.sidebar:
    st.markdown("## ✈ Aviation Analytics")

    st.markdown("---")

    # This is the ONLY navigation control
    menu = st.radio(
        "Main Menu",
        ["🏠 Dashboard", "🌦️ Weather Analysis", "🤖 AI Risk Prediction","🛰️ ATC Guidance Monitor"],
        key="navigation"
    )
        
    st.markdown("---")
        

    if menu=="🤖 AI Risk Prediction":
        # Only Live data for module 3 
        data_mode = st.radio(
        "📡 Data Source",
        ["Live Data"],
        index=0,
        key="mod3_data_mode"
        )
    elif menu=="🛰️ ATC Guidance Monitor" :
        data_mode = st.radio(
        "📡 Data Source",
        ["Live Data"],
        index=0,
        key="mod3_data_mode"
        )
    else:
        data_mode = st.radio(
        "📡 Data Source",
        ["Historical Data", "Live Data"],
        key="main_data_mode"
        )
            
    # --- Static Bottom Icons ---
    # We use st.container to push these to the bottom (or just place at the end of sidebar)
    st.markdown("<br>" * 10, unsafe_allow_html=True) # Spacer to push icons down
    st.markdown("---")
    
    icon_col1, icon_col2, icon_col3 = st.columns(3)
    with icon_col1:
        st.markdown("🏠")
    with icon_col2:
        st.markdown("⚙️")
    with icon_col3:
        st.markdown("📡")

load_css()
# Routing
if menu=="🏠 Dashboard":
    render_dashboard()
# --------------- RENDER MODULE 2 ---------------------
elif menu=="🌦️ Weather Analysis":
    from modules.dashboard import dfs,AIRPORT_ICAO_MAP,build_live_processed_df
    selected_airport=(st.session_state.selected_airport if "selected_airport" in st.session_state else "JFK")

    # -------- Select airport ------------
    if data_mode=="Historical Data":
    
        df=dfs[selected_airport]        # Historical datasets
        mode="Historical Data"  
    else:
    
        icao = AIRPORT_ICAO_MAP[selected_airport]
        minutes=st.session_state.live_window_minutes if "live_window_minutes" in st.session_state else 60     
        df=build_live_processed_df(
                icao=icao,
                airport_name=selected_airport,
                minutes=minutes)
        mode="Live Data"
    render_module2(df,mode)
# --------------- RENDER MODULE 3 ---------------------
elif menu=="🤖 AI Risk Prediction":
    from live.live_flight_data import fetch_live_flights_with_weather
    
    df_flight_data=fetch_live_flights_with_weather()
    render_module3(df_flight_data) 

else:
    render_module4()
        
