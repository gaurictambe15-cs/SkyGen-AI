# MODULE 2
# WEATHER PARAMETER ANALYSIS
import streamlit as st
import pandas as pd
import plotly.express as px
from live.live_weather_logic import (filter_live,add_status_column,generate_live_insight,THRESHOLDS)

def render_module2(df,mode):
    """
    MODULE 2 — WEATHER PARAMETER ANALYSIS
    Main window UI only.
    """

    # ==================================================
    # 1️⃣ PARAMETER CONTROL CARD
    # ==================================================

    st.markdown("""
    <div class="topbar">
    <div><h2>🌦️ Weather Parameter Analysis</h2>
    </div></div>""",unsafe_allow_html=True)

    st.markdown("""<div class="card"><div class="class-content"><h4>Controls</h4>""", unsafe_allow_html=True)
        
    col1, col2 = st.columns(2)

    with col1:
        parameter = st.selectbox(
            "Select Parameter",
            ["Wind Speed", "Visibility", "Precipitation"],
            key="m2_parameter"
        )
        if parameter=="Wind Speed":
            parameter="wind_speed"
        elif parameter=="Visibility":
            parameter="visibility"
        elif parameter=="Precipitation":
                parameter="precip"
    with col2:
        if mode == "Historical":
            date_range = st.slider(
                "Select Time Range",
                min_value=df["timestamp"].min().date(),
                max_value=df["timestamp"].max().date(),
                value=(
                    df["timestamp"].min().date(),
                    df["timestamp"].max().date()
                ),
                key="m2_date_range"
            )
        else:
            minutes = st.selectbox(
                "Recent live window",
                [60, 120, 130,140,150,160],
                key="m2_live_window"
            )

    # ==================================================
    # 2️⃣ FILTER DATA
    # ==================================================

    if mode == "Historical":
        start, end = date_range
        df_filtered = df[
            (df["timestamp"].dt.date >= start) &
            (df["timestamp"].dt.date <= end)
        ]
    else:
        if "timestamp" not in df.columns:
            import datetime
            now=datetime.datetime.now()
            df["timestamp"]=[now-datetime.timedelta(minutes=i) for i in reversed(range(len(df)))]
            

            df["timestamp"]=pd.to_datetime(df["timestamp"],errors='coerce')
            
            latest_time=df["timestamp"].max()
            df_filtered=df[df["timestamp"]>=latest_time-pd.Timedelta(minutes=minutes)]

        df_filtered = filter_live(df, minutes)
        
    df_filtered = add_status_column(df_filtered, parameter)

    # ==================================================
    # 3️⃣ MAIN WEATHER CHART CARD
    # ==================================================
    st.markdown("<br>",unsafe_allow_html=True)
    
    fig=px.line(
        df_filtered,
        x="timestamp",
        y=parameter,
        title=f"{parameter.replace('_',' ').title()} vs Time"
    )
    
    with st.container(border=True):
        st.markdown("Parameter Vs. Time")
        st.markdown(f"### {parameter.replace('_',' ').title()} vs Time")
        st.plotly_chart(fig,use_container_width=True,key="mod2_line_chart")
        st.markdown("""</div></div>""", unsafe_allow_html=True)

    # Threshold lines
    caution = THRESHOLDS[parameter]["caution"]
    critical = THRESHOLDS[parameter]["critical"]

    fig.add_hline(y=caution, line_dash="dash", line_color="orange", annotation_text="Caution")
    fig.add_hline(y=critical, line_dash="dash", line_color="red", annotation_text="Critical")

    
    
    with st.container(border=True):
        st.markdown("Threshold Line Graph")
        st.markdown(f"### {parameter.replace('_',' ').title()} vs Time")
        st.plotly_chart(fig, use_container_width=True,key="mod2_dash_chart")
        st.markdown("""</div></div>""", unsafe_allow_html=True)

    # Zone distribution
    
    if not df_filtered.empty:

        # Count zones
        zone_counts = df_filtered["status"].value_counts()
        total_points = len(df_filtered)

        normal_minutes = zone_counts.get("Normal", 0)
        caution_minutes = zone_counts.get("Caution", 0)
        critical_minutes = zone_counts.get("Critical", 0)

        # Convert to %
        normal_pct = round((normal_minutes / total_points) * 100, 1)
        caution_pct = round((caution_minutes / total_points) * 100, 1)
        critical_pct = round((critical_minutes / total_points) * 100, 1)

        import plotly.graph_objects as go

        fig_zone = go.Figure()

        fig_zone.add_trace(go.Bar(
            x=[normal_pct, caution_pct, critical_pct],
            y=["Normal", "Caution", "Critical"],
            orientation="h",
            text=[
                f"{normal_pct}% ({normal_minutes} min)",
                f"{caution_pct}% ({caution_minutes} min)",
                f"{critical_pct}% ({critical_minutes} min)"
            ],
            textposition="auto"
        ))

        fig_zone.update_layout(
            title="Zone Exposure (Selected Window)",
            xaxis_title="Percentage of Time",
            yaxis_title="Zone",
            height=320
        )

        
    with st.container(border=True):
        st.markdown("Zone Distribution")
        st.plotly_chart(fig_zone, use_container_width=True, key="zone_distribution")
        st.markdown("""</div></div>""", unsafe_allow_html=True)
    
    # ==================================================
    # 4️⃣ INSIGHT TEXT CARD
    # ==================================================
    
    insight = generate_live_insight(df_filtered)
    
    st.markdown(f"""<div class="card"><div class="card-content">
    <h3>Weather Insight</h3>
    <p>{insight}</p>
    </div></div>""",unsafe_allow_html=True)

    # ==================================================
    # 5️⃣ OPTIONAL WEATHER STATUS STRIP
    # ==================================================
    
    if not df_filtered.empty:
        current_status = df_filtered["status"].iloc[-1]

        if current_status == "Critical":
            icon = "🔴"
        elif current_status == "Caution":
            icon = "🟠"
        else:
            icon = "🟢"
        
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown(f"""<div class="card"><div class="card-content">
        <h3>Current Weather Status</h3>
        <p>{icon}<strong>{current_status}</strong></p>
        </div></div>""",unsafe_allow_html=True)

