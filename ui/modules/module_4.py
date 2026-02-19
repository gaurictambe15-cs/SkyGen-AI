# Module 4
import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.express as px
from live.atc_decision_logic import (
    fetch_recent_data,
    get_top_critical_flights,
    generate_suggested_actions,
    operational_trend_strip,
    prepare_heatmap_data
)

def render_module4():

    # -----------------------------
    # Top Bar: Time window + Flight selection
    # -----------------------------
    st.markdown(
        """
        <div class="topbar">
        <div><h2>🛰️ ATC Guidance Monitor </h2></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(f"""<div class="card"><div class="class-content">
                <h4>🏢 Airport Info</h4>
                <p>John F. Kennedy International Airport (JFK) - New York International Airport</p>
                """, unsafe_allow_html=True)
   
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    selected_airport = "JFK"
    
    selected_phase = st.selectbox(
        "Select Flight Phase 🛫🛬", ["Takeoff", "Landing"], index=0, key="m4_phase"
    )
    
    # -----------------------------
    # Fetch Data
    # -----------------------------
    df = fetch_recent_data(selected_airport)
    critical_flights_df=get_top_critical_flights(df,phase=selected_phase,top_n=5)
    
    # ------------------- Critical Flights Card -------------------
     # Assume selected phase and df are passed from app.py
    critical_flights_df = get_top_critical_flights(df, phase=selected_phase, top_n=5)
    with st.container(border=True):
        st.markdown("""<div class="card" style='border:2px solid #1a237e; border-radius:10px; padding:10px; margin-bottom:10px;'>
                    <h4>🚨 Top Critical Flights</h4>""", unsafe_allow_html=True)
        st.dataframe(critical_flights_df,use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------- Suggested Actions Card -------------------
    actions_df = generate_suggested_actions(df, phase=selected_phase).head(20)
    with st.container(border=True):
        st.markdown("""<div class="card" style='border:2px solid #1a237e; border-radius:10px; padding:10px; margin-bottom:10px;'>
                    <h4>📜 Suggested Actions</h4>""", unsafe_allow_html=True)
        st.dataframe(actions_df,use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Middle Row: 3 Graphs Side-by-Side ---
    trends = operational_trend_strip(df, minutes=60)

    st.markdown("""<div class="card" style='border:2px solid #ffa500; border-radius:10px; padding:10px; margin-bottom:10px;'><h4>📊 Live Operational Trends</h4>""", unsafe_allow_html=True)
    t_col1, t_col2, t_col3 = st.columns(3)
    
    for i, (param, data) in enumerate(trends.items()):
        target_col = [t_col1, t_col2, t_col3][i]
        with target_col:
            
            trend_df = pd.DataFrame({"Time": data["timestamps"], "Value": data["values"]})
            fig = px.line(trend_df, x="Time", y="Value", markers=True, title=param.title())
            fig.add_hline(y=data["caution"], line_dash="dash", line_color="orange")
            fig.add_hline(y=data["critical"], line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Bottom Row: Stats (Left) and Heatmap (Right) ---
    b_left, b_right = st.columns(2)
    
    with b_left:
        st.markdown("""<div class="card" style='border:2px solid #ff5722; border-radius:10px; padding:10px; margin-bottom:10px;'>
                    <h4>✈️ ATC Decisions</h4>""", unsafe_allow_html=True)
        if not critical_flights_df.empty:
            # Display flight info
            st.dataframe(
            critical_flights_df[["flight_number", "flight_timestamp"]],
            use_container_width=True
        )

            # Generate ATC suggested actions for these flights
            atc_actions_df = generate_suggested_actions(critical_flights_df, phase=selected_phase)

            if not atc_actions_df.empty:
                for idx, row in atc_actions_df.iterrows():
                    st.markdown(f"*{row['Flight']} → {row['Action']}*")
            else:
                st.info("No ATC actions required for current critical flights.")
        else:
            st.info("No critical flights at the moment.")

        st.markdown("</div>", unsafe_allow_html=True)

    with b_right:
        st.markdown("""<div class="card" style='border:2px solid #ff5722; border-radius:10px; padding:10px; margin-bottom:10px;'>
                    <h4>🗺️ Flight vs Parameter Heatmap</h4>""", unsafe_allow_html=True)
        
        heatmap_df = prepare_heatmap_data(df, minutes=60)
        if heatmap_df is not None:
            fig = px.imshow(
                heatmap_df,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Viridis",
                labels=dict(x="Flight Number",y="Weather Parameter",color="Value")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No recent data to show heatmap.")
        st.markdown("</div>", unsafe_allow_html=True)
    # --- Final Row: Centered Download Button ---
    st.markdown("---") # Visual separator
    _, d_center, _ = st.columns([1, 1, 1]) # Create a center-focused column
    with d_center:
        st.markdown("""<div class="card" style='border:2px solid #1a237e; border-radius:10px; padding:10px; margin-bottom:10px;'>
                    <h4>📥 Download Full Operational Report (CSV)</h4>""", unsafe_allow_html=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="download",
            data=csv,
            file_name="JFK_ATC_Operational_Report.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)