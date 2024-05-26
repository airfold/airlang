import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from streamlit_extras.colored_header import colored_header

# Streamlit app configuration
st.set_page_config(
    page_title="LLM Monitoring",
    layout="wide",
    page_icon="📊",
    menu_items={"Get help": "https://github.com/airfold/airlang", "About": "https://www.airfold.co"},
)

# Title and description
colored_header(
    label="LLM Monitoring",
    description="Use the filters to select specific date ranges, models, and group IDs to view the corresponding metrics.",
    color_name="red-70",
)

# Constants and environment variables
api_url = "https://api.airfold.co/v1"
api_token = os.getenv("AIRFOLD_API_KEY")

# Date range options
date_options = {
    "15 mins": timedelta(minutes=15),
    "30 mins": timedelta(minutes=30),
    "1 hour": timedelta(hours=1),
    "3 hours": timedelta(hours=3),
    "12 hours": timedelta(hours=12),
    "24 hours": timedelta(days=1),
    "2 days": timedelta(days=2),
    "7 days": timedelta(days=7),
    "30 days": timedelta(days=30),
}


def pipe_to_df(pipe, params=None, api_token=None):
    if not api_token:
        api_token = os.getenv("AIRFOLD_API_KEY")

    url = f"https://api.airfold.co/v1/pipes/{pipe}.json"
    headers = {"Authorization": f"Bearer {api_token}"}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data)
        return df
    else:
        response.raise_for_status()


def get_total_metrics(api_token=None):
    return pipe_to_df("metrics_all_time", api_token=api_token)


def get_metrics(
    start_date: datetime = None,
    end_date: datetime = None,
    models=None,
    groups=None,
    delta=None,
    interval=None,
    api_token=None,
):
    models = models or ""
    groups = groups or ""

    if delta is not None:
        end_date = datetime.now()
        start_date = end_date - delta
    else:
        end_date = end_date or datetime.now()
        start_date = start_date or end_date - timedelta(days=7)

    params = {
        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
    }
    if models:
        params["models"] = models
    if groups:
        params["groups"] = groups

    df = pipe_to_df("metrics_total", params=params, api_token=api_token)
    df["ts"] = pd.to_datetime(df["ts"])

    # Convert relevant columns to integers
    int_columns = [
        "request_count",
        "total_prompt_tokens",
        "total_completion_tokens",
        "total_cost",
    ]
    df[int_columns] = df[int_columns].astype(float)

    if not interval:
        if delta < timedelta(hours=1):
            interval = "5t"
        elif delta < timedelta(days=2):
            interval = "15t"
        elif delta < timedelta(days=7):
            interval = "1h"
        else:
            interval = "1d"

    df.set_index("ts", inplace=True)
    df = (
        df.resample(interval)
        .agg(
            {
                "request_count": "sum",
                "generation_time_p50": "mean",
                "generation_time_p95": lambda x: x.quantile(0.95),
                "total_prompt_tokens": "sum",
                "total_completion_tokens": "sum",
                "tokens_per_sec_p50": "mean",
                "tokens_per_sec_p95": lambda x: x.quantile(0.95),
                "total_cost": "sum",
            }
        )
        .reset_index()
    )

    return df


# Sidebar for filters
with st.sidebar:
    st.image(
        "https://i.gyazo.com/b8ea59576765a4b5065b8cf1ef9e701d.png",
        width=200,
    )

    st.header("Filters")

    # Date range slider
    date_range = st.select_slider("Select Date Range", options=list(date_options.keys()), value="7 days")
    selected_duration = date_options[date_range]

    end_date = datetime.now()
    start_date = end_date - selected_duration

    # Fetch available models and groups
    headers = {"Authorization": f"Bearer {api_token}"}
    models, groups = [], []

    # Fetch groups
    response = requests.get(f"{api_url}/pipes/groups.json", headers=headers)
    if response.status_code == 200:
        data = response.json().get("data", [])
        groups.extend([row["group_id"] for row in data])
    else:
        st.error(f"Error fetching groups: {response.status_code} - {response.text}")

    # Fetch models
    response = requests.get(f"{api_url}/pipes/models.json", headers=headers)
    if response.status_code == 200:
        data = response.json().get("data", [])
        models.extend([row["model"] for row in data])
    else:
        st.error(f"Error fetching models: {response.status_code} - {response.text}")

    # Multi-select boxes for models and groups
    selected_models = st.multiselect("Filter by Model", models, default=[])
    selected_groups = st.multiselect("Filter by Group ID", groups, default=[])

    # Refresh button
    refresh_button = st.button("Refresh")


df = get_metrics(start_date, end_date, selected_models, selected_groups, api_token=api_token, delta=selected_duration)
total_df = get_total_metrics(api_token=api_token)

print(df)


# Display high-level metrics
def display_metrics(df):
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Requests", total_df["request_count"][0])
        col2.metric("Total Cost", "$" + str(round(total_df["total_cost"][0], 2)))
        col3.metric("Average Generation Time", str(total_df["generation_time_p50"][0]) + "s")
        col4.metric("Average Tokens per Second", round(total_df["tokens_per_sec_p50"][0], 2))


# Display charts
def display_charts(df):
    if not df.empty:
        col1, col2 = st.columns(2)
        fig1 = px.line(df, x="ts", y="request_count", title="Total Requests")
        col1.plotly_chart(fig1)

        fig4 = px.line(df, x="ts", y="total_cost", title="Total Cost")
        col1.plotly_chart(fig4)

        fig2 = px.line(
            df,
            x="ts",
            y=["generation_time_p50", "generation_time_p95"],
            title="Generation Time",
            labels={"value": "Generation Time", "variable": "Metric"},
        )
        col2.plotly_chart(fig2)

        fig3 = px.line(
            df,
            x="ts",
            y=["tokens_per_sec_p50", "tokens_per_sec_p95"],
            title="Tokens/sec",
            labels={"value": "Tokens per Second", "variable": "Metric"},
        )
        col2.plotly_chart(fig3)


# Main content
with st.spinner("Loading data..."):
    display_metrics(df)
    display_charts(df)
