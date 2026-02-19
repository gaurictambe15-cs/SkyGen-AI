# module_3.py
import streamlit as st
import pandas as pd
import plotly.express as px
from live.ai_risk_logic import train_threshold_model,predict_risk_live,get_live_flight_risk


def render_module3(df_flight_data):
    
    # -----------------------------
    # Top Bar: Time window + Flight selection
    # -----------------------------
    st.markdown(
        """
        <div class="topbar">
        <div><h2>🤖 AI Risk Prediction — Live Flights</h2></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card" style='border:2px solid #1a237e; border-radius:10px; padding:10px; margin-bottom:10px;'>
                    <h4>Select Live Window</h4>""", unsafe_allow_html=True)
        time_options = [60, 70, 80, 90, 100, 110, 120]  # minutes
        minutes = st.selectbox(
            "Recent window (minutes)",
            options=time_options,
            index=0,
            key="time_window"
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card" style='border:2px solid #1a237e; border-radius:10px; padding:10px; margin-bottom:10px;'>
                    <h4>Select Number Of Flights</h4>""", unsafe_allow_html=True)
        num_options = [5, 10, 15, 20]
        num_display = st.selectbox(
            "Select number of flights to display",
            options=num_options,
            index=0,
            key="num_flights"
        )
        st.markdown("</div>", unsafe_allow_html=True)
    # -----------------------------
    # Fetch Live Flight Risk Data
    # -----------------------------
    

    with st.spinner("Fetching live flights & predicting risk..."):
        df_risk_live = get_live_flight_risk(df_flight_data, num_display=None)

    if df_risk_live.empty:
        st.warning("No live flights detected at the moment.")
        return
    
    

    # -----------------------------
    # Slice top flights for all downstream outputs
    # -----------------------------
    df_risk_live_display = df_risk_live.head(num_display)

    # -----------------------------
    # Flight Risk Overview
    # -----------------------------
    
        
    risk_class={
        "Normal":"green",
        "caution":"orange",
        "Critical":"red"
    }
    with st.container(border=True):
        st.markdown("""
        <div class="card" style='border:2px solid #1a237e; border-radius:10px; padding:10px; margin-bottom:10px;'>
            <h4>✈️ Flight Risk Overview</h4>
        """, unsafe_allow_html=True)

        for idx, row in df_risk_live_display.iterrows():
            
            st.markdown(
                f"""
                <div style='border:1px solid #ccc; border-radius:8px; padding:10px; margin-bottom:10px;'>
                    <h4>✈︎ Flight: {row['flight_number']}</h4>
                    <p>Predicted Risk: <strong >{row['predicted_risk']}</strong> </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------
    # Explainable Insights
    # -----------------------------
    with st.container(border=True):
        st.markdown("""
        <div class="card" style='border:2px solid #1a237e; border-radius:10px; padding:10px; margin-bottom:10px;'>
            <h4>📊 Explainable Insights</h4>
        """, unsafe_allow_html=True)
        
        for idx, row in df_risk_live_display.iterrows():
            st.markdown(
                f"""
                <div style='border:1px solid #ddd; border-radius:6px; padding:8px; margin-bottom:8px;'>
                    <p style="font-weight:700;color:#1a237e"><strong>Flight:</strong> {row['flight_number']}</p>
                    <p><strong>Wind Speed:</strong> {row['wind_speed']:.1f} m/s</p>
                    <p><strong>Visibility:</strong> {row['visibility']:.1f} km</p>
                    <p><strong>Precipitation:</strong> {row['precip']:.1f} mm/hr</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------
    # What-If / Scenario Simulation
    # -----------------------------
    with st.container(border=True):
        st.markdown("""
        <div class="card" style='border:2px solid #ffa500; border-radius:10px; padding:10px; margin-bottom:10px;'>
                    <h4>🔃 What-If / Scenario Simulation</h4>""", unsafe_allow_html=True)

        
        # Copy the selected flights slice
        df_sim = df_risk_live_display.copy()

        # Scenario sliders
        col1, col2, col3 = st.columns(3)

        with col1:
            wind_delta = st.slider("Wind Speed Change (m/s)", 0.0, 20.0, 0.0, 0.5, key="wind_slider")
        with col2:
            visibility_delta = st.slider("Visibility Change (km)", 0.0, 20.0, 0.0, 0.5, key="vis_slider")
        with col3:
            precip_delta = st.slider("Precipitation Change (mm/hr)", 0.0, 20.0, 0.0, 0.1, key="precip_slider")

        
        # Apply scenario changes with clipping to ensure no negative values
        for col, delta in [("wind_speed", wind_delta), ("visibility", visibility_delta), ("precip", precip_delta)]:
            if col in df_sim.columns:
                df_sim[col] = (df_sim[col] + delta).clip(lower=0)

        # Recompute risk for this scenario
        model = train_threshold_model()
        df_sim_risk = predict_risk_live(df_sim, model)
        st.markdown("</div>", unsafe_allow_html=True)

    # Display scenario results
    with st.container(border=True):
        st.markdown("""
        <div class="card" style='border:2px solid #ff5722; border-radius:10px; padding:10px; margin-bottom:10px;'>
                    <h4>📌 Scenario Risk Predictions</h4>""", unsafe_allow_html=True)
        
        risk_color = {"Normal": "#4CAF50", "Caution": "#FFA500", "Critical": "#F44336"}
        for idx, row in df_sim_risk.iterrows():
            st.markdown(
                f"""
                <div style='border:1px solid #ccc; border-radius:8px; padding:10px; margin-bottom:10px;'>
                <h4>Flight: {row['flight_number']}</h4>
                <p>Predicted Risk under scenario: 
                <strong style='color:{risk_color.get(row['predicted_risk'], "black")}'>{row['predicted_risk']}</strong></p>
                <p>Wind: {row['wind_speed']:.1f} m/s | Visibility: {row['visibility']:.1f} km | Precip: {row['precip']:.1f} mm/hr</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # Show ATC-friendly bullet points
    with st.container(border=True):
        st.markdown("""
        <div class="card" style='border:2px solid #673ab7; border-radius:10px; padding:10px; margin-bottom:10px;'>
                    <h4>🧾Impact Summary</h4>""", unsafe_allow_html=True)
        
        risk_color = {
        "Normal": "#4CAF50",
        "Caution": "#FFA500",
        "Critical": "#F44336"
        }
        for idx, row in df_sim_risk.iterrows():
            st.markdown(
            f"""
            <p>
                <span style="font-weight:700; color:#000000;">
                    Flight {row['flight_number']}
                </span>
                : Predicted risk →
                <span style="color:{risk_color.get(row['predicted_risk'], '#000000')}; font-weight:500;">
                    {row['predicted_risk']}
                </span>
            </p>
            """,
            unsafe_allow_html=True
            )
            
        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------
    # Suggested Actions
    # -----------------------------
    with st.container(border=True):
        st.markdown("""
        <div class="card" style='border:2px solid #009688; border-radius:10px; padding:10px; margin-bottom:10px;'>
                    <h4>📝 Suggested Actions</h4>""", unsafe_allow_html=True)

        action_color = {
        "Normal": "#4CAF50",
        "Caution": "#FFA500",
        "Critical": "#F44336"
        }
        for idx, row in df_sim_risk.iterrows():
            action = "Maintain route" if row['predicted_risk']=="Normal" else \
                    "Monitor weather closely" if row['predicted_risk']=="Caution" else \
                    "Adjust flight path. Hold at safe altitude. Notify pilots immediately !"
            st.markdown(f"""
                        <p>
                        <span style="font-weight:700; color:#000000;">
                        {row['flight_number']}:
                        </span>
                        <span style="color:{action_color.get(row['predicted_risk'], '#000000')};">
                        {action}
                        </span>
                        </p>
                        """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
    # -----------------------------
    # Download CSV
    # -----------------------------
    with st.container(border=True):
        st.markdown("""<div class="card" style='border:2px solid #1a237e; border-radius:10px; padding:10px; margin-bottom:10px;'>
                    <h4>💾 Download CSV</h4>""", unsafe_allow_html=True)
        csv_data = df_sim_risk.to_csv(index=False)
        st.download_button("Download Selected Flights CSV", data=csv_data, file_name="flight_risk.csv")
        st.markdown("</div></div>", unsafe_allow_html=True)