"""
dashboard/app.py — Sales Intelligence Dashboard (équivalent Power BI)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

DB_PATH = os.path.join("data", "sales.db")

st.set_page_config(page_title="Sales Intelligence", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .kpi-card { background:white; border-radius:12px; padding:1.2rem;
                box-shadow:0 2px 8px rgba(0,0,0,.08); text-align:center; }
    .kpi-value { font-size:2rem; font-weight:700; color:#2c3e50; }
    .kpi-label { color:#7f8c8d; font-size:.85rem; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Sales Intelligence Dashboard")
st.caption("Pipeline CRM → Insights temps réel • Réduction reporting: 80%")


@st.cache_data(ttl=300)
def load():
    if not os.path.exists(DB_PATH):
        # Bootstrap automatique
        import subprocess
        subprocess.run(["python", "etl/pipeline.py"])
    conn = sqlite3.connect(DB_PATH)
    opps     = pd.read_sql("SELECT * FROM opportunities", conn)
    accounts = pd.read_sql("SELECT * FROM accounts", conn)
    conn.close()
    return opps, accounts


try:
    opps, accounts = load()
except Exception:
    st.error("Base de données introuvable. Lancez `python etl/pipeline.py`")
    st.stop()

# ── FILTERS ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Filtres")
    stages   = st.multiselect("Étapes", opps["stage"].unique(), default=list(opps["stage"].unique()))
    owners   = st.multiselect("Commercial", opps["owner"].unique(), default=list(opps["owner"].unique()))
    products = st.multiselect("Produit", opps["product_line"].unique(), default=list(opps["product_line"].unique()))

filtered = opps[opps["stage"].isin(stages) & opps["owner"].isin(owners) & opps["product_line"].isin(products)]

# ── KPIs ─────────────────────────────────────────────────────────────────────
won  = filtered[filtered["stage"] == "Closed Won"]
lost = filtered[filtered["stage"] == "Closed Lost"]
pipe = filtered[~filtered["stage"].isin(["Closed Won","Closed Lost"])]
closed = pd.concat([won, lost])
win_rate = len(won)/len(closed)*100 if len(closed) > 0 else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 Revenus", f"${won['amount'].sum():,.0f}")
c2.metric("📈 Pipeline", f"${pipe['amount'].sum():,.0f}")
c3.metric("🎯 Win Rate", f"{win_rate:.1f}%")
c4.metric("📋 Deals", len(filtered))
c5.metric("💵 Avg Deal", f"${won['amount'].mean():,.0f}" if len(won) > 0 else "$0")

st.divider()

# ── CHARTS ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    funnel = filtered.groupby("stage").agg(count=("opp_id","count"), value=("amount","sum")).reset_index()
    stage_order = ["Prospecting","Qualification","Proposal","Negotiation","Closed Won","Closed Lost"]
    funnel["stage"] = pd.Categorical(funnel["stage"], categories=stage_order, ordered=True)
    funnel = funnel.sort_values("stage")
    fig = go.Figure(go.Funnel(
        y=funnel["stage"], x=funnel["count"],
        textposition="inside", textinfo="value+percent initial",
        marker_color=["#3498db","#2ecc71","#f39c12","#e67e22","#27ae60","#e74c3c"]
    ))
    fig.update_layout(title="Funnel Commercial")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    rev_by_product = won.groupby("product_line")["amount"].sum().reset_index()
    fig2 = px.pie(rev_by_product, names="product_line", values="amount",
                title="Revenus par Produit", hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    filtered["close_date"] = pd.to_datetime(filtered["close_date"], errors="coerce")
    monthly = won.copy()
    monthly["month"] = pd.to_datetime(monthly["close_date"]).dt.to_period("M").astype(str)
    monthly_rev = monthly.groupby("month")["amount"].sum().reset_index()
    fig3 = px.bar(monthly_rev, x="month", y="amount",
                title="Revenus Mensuels (Closed Won)", color_discrete_sequence=["#2ecc71"])
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    by_owner = won.groupby("owner").agg(revenue=("amount","sum"), deals=("opp_id","count")).reset_index()
    fig4 = px.bar(by_owner.sort_values("revenue", ascending=True),
                x="revenue", y="owner", orientation="h",
                title="Performance par Commercial", color="revenue",
                color_continuous_scale="Teal")
    st.plotly_chart(fig4, use_container_width=True)

# ── TABLE ─────────────────────────────────────────────────────────────────────
st.subheader("📋 Opportunités récentes")
st.dataframe(
    filtered.sort_values("close_date", ascending=False).head(50)[
        ["opp_id","opp_name","stage","amount","owner","product_line","close_date"]
    ],
    use_container_width=True
)