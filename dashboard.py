import os

import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("LLM Metrics Dashboard")

api_url = "https://api.airfold.co/v1"
api_token = os.environ["AIRFOLD_API_KEY"]

end_date = datetime.now().date()
start_date = end_date - timedelta(days=7)
groups = ["<None>"]
models = ["<None>"]

cols = st.columns(4)
with cols[0]:
    start_date = st.date_input("Start Date", value=start_date)
with cols[1]:
    end_date = st.date_input("End Date", value=end_date)

top_graph = st.empty()
with top_graph.container(height=500):
    st.write("Loading graph...")
    st.spinner(text="")
col1, col2, col3 = st.columns(3)
with col1:
    left_graph = st.empty()
with col2:
    middle_graph = st.empty()
with col3:
    right_graph = st.empty()

headers = {"Authorization": f"Bearer {api_token}"}
date_range = pd.date_range(start=start_date, end=end_date, freq="D")
df = pd.DataFrame(columns=["date"])

response = requests.get(f"{api_url}/pipes/groups.json", headers=headers)
if response.status_code == 200:
    data = response.json()
    if data["data"]:
        groups.extend([row["group_id"] for row in data["data"]])
    else:
        st.error(f"Error: {response.status_code} - {response.text}")

response = requests.get(f"{api_url}/pipes/models.json", headers=headers)
if response.status_code == 200:
    data = response.json()
    if data["data"]:
        models.extend([row["model"] for row in data["data"]])
    else:
        st.error(f"Error: {response.status_code} - {response.text}")

if 'selected_model' not in st.session_state:
    st.session_state.selected_model = models[0]
if 'selected_group' not in st.session_state:
    st.session_state.selected_group = groups[0]
with cols[2]:
    model = st.selectbox("Filter by model", models, key="model_select")
    if model != st.session_state.selected_model:
        st.session_state.selected_model = model
with cols[3]:
    group = st.selectbox("Filter by group id", groups, key="group_select")
    if group != st.session_state.selected_group:
        st.session_state.selected_group = group

for date in date_range:
    start_time = date.isoformat()
    end_time = (date + timedelta(days=1)).isoformat()

    params = {"start_time": start_time, "end_time": end_time}
    if model != "<None>":
        params["model"] = model
    if group != "<None>":
        params["group"] = group
    response = requests.get(f"{api_url}/pipes/metrics_total.json", headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            row = dict([(k, v if v is not None else 0) for k,v in data["data"][0].items()])
            df = df._append({"date": date.date(), **row}, ignore_index=True)
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        break

request_count_chart = (
    alt.Chart(df)
    .mark_line()
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("request_count:Q", title="Request Count"),
        tooltip=["date", "request_count"],
    )
    .interactive()
)

generation_time_chart = (
    alt.Chart(df)
    .transform_calculate(**{
        "p50": "datum.generation_time_p50",
        "p95": "datum.generation_time_p95",
    })
    .transform_fold(["p50", "p95"])
    .mark_line()
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("value:Q", title="Generation Time (ms)"),
        color=alt.Color("key:N", title="Percentile"),
    )
    .interactive()
)

tokens_per_sec_chart = (
    alt.Chart(df)
    .transform_calculate(**{
        "p50": "datum.tokens_per_sec_p50",
        "p95": "datum.tokens_per_sec_p95",
    })
    .transform_fold(["p50", "p95"])
    .mark_line()
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("value:Q", title="Tokens per Second"),
        color=alt.Color("key:N", title="Percentile"),
    )
    .interactive()
)

total_cost_chart = (
    alt.Chart(df)
    .mark_line()
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("total_cost:Q", title="Total Cost, $"),
        tooltip=["date", "total_cost"],
    )
    .interactive()
)

top_graph.altair_chart(request_count_chart, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    left_graph.altair_chart(generation_time_chart, use_container_width=True)
with col2:
    middle_graph.altair_chart(tokens_per_sec_chart, use_container_width=True)
with col3:
    right_graph.altair_chart(total_cost_chart, use_container_width=True)
