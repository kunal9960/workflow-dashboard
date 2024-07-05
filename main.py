import random
import duckdb
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(page_title="Sales Dashboard", page_icon="dashboard.png", layout="wide")


col1, col2 = st.columns([1, 2])
with col1:
    st.write("<h2><b>📉 <u>Workflow Sales Dashboard</b></h2>", unsafe_allow_html=True)
    st.write(
        "<i>A sales dashboard featuring performance visuals and important financial data to understand the company's economic dynamics.</i>",
        unsafe_allow_html=True,
    )
with col2:
    st.image("header.gif", width=255)
st.divider()

st.write("<h2><b>⚙️ <u>Configuration</b></h2>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose a file")


@st.cache_data
def load_data(path: str):
    df = pd.read_excel(path)
    return df


if uploaded_file is None:
    default_path = "Financial Data Clean.xlsx"
    df = load_data(default_path)
    st.info("Using a random Sales Data for an example, Upload a file to use your own data 👇", icon="ℹ️")
else:
    df = load_data(uploaded_file)

all_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

with st.expander("🔭 Data Preview", expanded=True):

    st.dataframe(df, column_config={"Year": st.column_config.NumberColumn(format="%d")})


def plot_metric(label, value, prefix="", suffix="", show_graph=False, color_graph=""):
    fig = go.Figure()
    fig.add_trace(
        go.Indicator(
            value=value,
            gauge={"axis": {"visible": False}},
            number={"prefix": prefix, "suffix": suffix, "font.size": 28},
            title={"text": label, "font": {"size": 24}},
        )
    )
    if show_graph:
        fig.add_trace(
            go.Scatter(
                y=random.sample(range(0, 101), 30),
                hoverinfo="skip",
                fill="tozeroy",
                fillcolor=color_graph,
                line={"color": color_graph},
            )
        )
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        margin=dict(t=30, b=0),
        showlegend=False,
        plot_bgcolor="white",
        height=100,
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_gauge(indicator_number, indicator_color, indicator_suffix, indicator_title, max_bound):
    fig = go.Figure(
        go.Indicator(
            value=indicator_number,
            mode="gauge+number",
            domain={"x": [0, 1], "y": [0, 1]},
            number={"suffix": indicator_suffix, "font.size": 26},
            gauge={"axis": {"range": [0, max_bound], "tickwidth": 1}, "bar": {"color": indicator_color}},
            title={"text": indicator_title, "font": {"size": 28}},
        )
    )
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=50, b=10, pad=8),
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_top_right():
    sales_data = duckdb.sql(
        f"""
        WITH sales_data AS (
            UNPIVOT ( 
                SELECT 
                    Scenario,
                    business_unit,
                    {','.join(all_months)} 
                    FROM df 
                    WHERE Year='2023' 
                    AND Account='Sales' 
                ) 
            ON {','.join(all_months)}
            INTO
                NAME month
                VALUE sales
        ),
        aggregated_sales AS (
            SELECT
                Scenario,
                business_unit,
                SUM(sales) AS sales
            FROM sales_data
            GROUP BY Scenario, business_unit
        )
        SELECT * FROM aggregated_sales
        """
    ).df()

    fig = px.bar(
        sales_data,
        x="business_unit",
        y="sales",
        color="Scenario",
        barmode="group",
        text="sales",
        title="Sales for Year 2023",
        height=400,
        color_discrete_map={"Budget": "rgba(148, 0, 211, 0.2)", "Forecast": "rgba(255, 255, 150, 0.5)"}
    )

    fig.update_traces(
        textfont_size=12, textangle=0, textposition="outside", cliponaxis=False
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_bottom_left():
    sales_data = duckdb.sql(
        f"""
        WITH sales_data AS (
            SELECT 
                Scenario,{','.join(all_months)} 
            FROM df 
            WHERE Year='2023' 
            AND Account='Sales'
            AND business_unit='Software'
        )
        UNPIVOT sales_data 
        ON {','.join(all_months)}
        INTO
            NAME month
            VALUE sales
        """
    ).df()
    fig = px.line(
        sales_data,
        x="month",
        y="sales",
        color="Scenario",
        markers=True,
        text="sales",
        title="Monthly Budget vs Forecast 2023",
        color_discrete_map={"Budget": "rgba(255, 99, 71, 0.5)", "Forecast": "rgba(135, 206, 235, 0.5)"}
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)


def plot_bottom_right():
    sales_data = duckdb.sql(
        f"""
        WITH sales_data AS (
            UNPIVOT ( 
                SELECT 
                    Account,Year,{','.join([f'ABS({month}) AS {month}' for month in all_months])}
                    FROM df 
                    WHERE Scenario='Actuals'
                    AND Account!='Sales'
                ) 
            ON {','.join(all_months)}
            INTO
                NAME year
                VALUE sales
        ),
        aggregated_sales AS (
            SELECT
                Account,
                Year,
                SUM(sales) AS sales
            FROM sales_data
            GROUP BY Account, Year
        )
        SELECT * FROM aggregated_sales
        """
    ).df()

    color_palette = [
        "#ADD8E6",
        "#FFD700",
        "#FFA07A",
        "#98FB98",
        "#FFB6C1",
        "#87CEFA",
        "#FFA500",
        "#F0E68C",
    ]
    color_discrete_map = {account: color_palette[i % len(color_palette)] for i, account in
                          enumerate(sales_data['Account'].unique())}

    fig = px.bar(
        sales_data,
        x="Year",
        y="sales",
        color="Account",
        title="Actual Yearly Sales Per Account",
        color_discrete_map=color_discrete_map
    )

    fig.update_layout(plot_bgcolor="white")

    st.plotly_chart(fig, use_container_width=True)


st.divider()
st.write("<h2><b>🚀 <u>Dashboard Preview</b></h2>", unsafe_allow_html=True)

top_left_column, top_right_column = st.columns((2, 1))
bottom_left_column, bottom_right_column = st.columns(2)


def plot_metric(label, value, prefix="", suffix="", show_graph=False, color_graph="", title_size=16):
    fig = go.Figure()
    fig.add_trace(
        go.Indicator(
            value=value,
            gauge={"axis": {"visible": False}},
            number={"prefix": prefix, "suffix": suffix, "font.size": 25},
            title={"text": label, "font": {"size": title_size}},
        )
    )
    if show_graph:
        fig.add_trace(
            go.Scatter(
                y=random.sample(range(0, 101), 30),
                hoverinfo="skip",
                fill="tozeroy",
                fillcolor=color_graph,
                line={"color": color_graph},
            )
        )
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        margin=dict(t=30, b=0),
        showlegend=False,
        plot_bgcolor="white",
        height=160,
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_metric_with_graph(label, value, prefix="", suffix="", graph_data=None, graph_color="", title_size=10):
    fig = go.Figure()
    fig.add_trace(
        go.Indicator(
            value=value,
            gauge={"axis": {"visible": False}},
            number={"prefix": prefix, "suffix": suffix, "font.size": 25},
            title={"text": label, "font": {"size": title_size}},
        )
    )
    if graph_data is not None:
        fig.add_trace(
            go.Scatter(
                x=np.arange(len(graph_data)),
                y=graph_data,
                mode="lines",
                line={"color": graph_color},
                fill="tozeroy",
                fillcolor=graph_color,
                hoverinfo="skip",
            )
        )
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        margin=dict(t=30, b=0),
        showlegend=False,
        plot_bgcolor="white",
        height=160,
    )
    st.plotly_chart(fig, use_container_width=True)


with top_left_column:
    column_1, column_2, column_3, column_4 = st.columns(4)
    with column_1:
        plot_metric(
            "Total Accounts Receivable",
            6621280,
            prefix="$",
            suffix="",
            show_graph=True,
            color_graph="rgba(0, 104, 201, 0.2)",
        )
        plot_gauge(1.86, "#0068C9", "%", "Current Ratio", 3)
    with column_2:
        plot_metric(
            "Total Accounts Payable",
            1630270,
            prefix="$",
            suffix="",
            show_graph=True,
            color_graph="rgba(255, 165, 0, 0.2)",
        )
        plot_gauge(10, "#FF8700", " days", "In Stock", 31)
    with column_3:
        plot_metric_with_graph(
            "Equity Ratio",
            75.38,
            prefix="",
            suffix=" %",
            graph_data=random.sample(range(0, 101), 30),
            graph_color="rgba(255, 43, 43, 0.2)",
            title_size=18,
        )
        plot_gauge(7, "#FF2B2B", " days", "Out Stock", 31)

    with column_4:
        plot_metric_with_graph(
            "Debt Equity",
            1.10,
            prefix="",
            suffix=" %",
            graph_data=random.sample(range(0, 101), 30),
            graph_color="rgba(43, 131, 59, 0.2)",
            title_size=18,
        )
        plot_gauge(28, "#29B09D", " days", "Delay", 31)
with top_right_column:
    plot_top_right()

with bottom_left_column:
    plot_bottom_left()

with bottom_right_column:
    plot_bottom_right()

st.markdown(
    "[![GitHub Badge](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=fff&style=flat)](https://github.com/kunal9960/workflow_dashboard)&nbsp;&nbsp;" +
    "[![Streamlit Badge](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=fff&style=flat)](https://workflow-dashboard-kunal.streamlit.app/)")


ft = """
<style>
a:link , a:visited{
color: #BFBFBF;  /* theme's text color hex code at 75 percent brightness*/
background-color: transparent;
text-decoration: none;
}

a:hover,  a:active {
color: #0283C3; /* theme's primary color*/
background-color: transparent;
text-decoration: underline;
}

#page-container {
  position: relative;
  min-height: 10vh;
}

footer{
    visibility:hidden;
}

.footer {
position: relative;
left: 0;
top:150px;
bottom: 0;
width: 100%;
background-color: transparent;
color: #808080;
text-align: left;
}
</style>

<div id="page-container">

<div class="footer">
<p style='font-size: 1em;'>Made with <a style='display: inline; text-align: left;' href="https://streamlit.io/" target="_blank">Streamlit</a><br 'style= top:3px;'>
with <img src="https://em-content.zobj.net/source/skype/289/red-heart_2764-fe0f.png" alt="heart" height= "10"/><a style='display: inline; text-align: left;' href="https://github.com/kunal9960" target="_blank"> by Kunal</a>
<a style='display: inline; text-align: left;'>© Copyright 2024</a></p>
</div>

</div>
"""
st.write(ft, unsafe_allow_html=True)