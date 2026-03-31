"""
etl/pipeline.py — Orchestration du pipeline ETL Sales Intelligence
"""

import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string

DB_PATH = os.path.join("data", "sales.db")
SCHEMA  = os.path.join("sql", "schema.sql")


# ─────────────────────────────────────────────────────────────────────────────
# EXTRACT
# ─────────────────────────────────────────────────────────────────────────────

def generate_crm_data(n_accounts=200):
    """Générer des données CRM réalistes synthétiques."""
    rng = np.random.default_rng(42)
    industries  = ["SaaS", "Finance", "Healthcare", "Retail", "Manufacturing", "Logistics"]
    countries   = ["France", "Côte d'Ivoire", "Sénégal", "Maroc", "Canada", "Belgique"]
    stages      = ["Prospecting","Qualification","Proposal","Negotiation","Closed Won","Closed Lost"]
    stage_probs = [0.20, 0.22, 0.18, 0.12, 0.18, 0.10]
    owners      = ["Alice Martin", "Bruno Diallo", "Chiara Rossi", "David Kone", "Elena Petit"]
    products    = ["Platform Pro", "Analytics Suite", "API Access", "Enterprise Bundle"]

    accounts = pd.DataFrame({
        "account_id":     [f"ACC{i:04d}" for i in range(n_accounts)],
        "company_name":   [f"Company_{i}" for i in range(n_accounts)],
        "industry":       rng.choice(industries, n_accounts),
        "country":        rng.choice(countries, n_accounts),
        "region":         rng.choice(["EMEA","APAC","AMER"], n_accounts),
        "employee_count": rng.integers(10, 5000, n_accounts),
        "annual_revenue": np.round(rng.uniform(100_000, 50_000_000, n_accounts), -3),
        "account_tier":   rng.choice(["Enterprise","Mid-Market","SMB"], n_accounts, p=[0.2,0.3,0.5]),
    })

    n_opp = n_accounts * 3
    base_date = datetime(2023, 1, 1)
    close_dates = [base_date + timedelta(days=int(d)) for d in rng.integers(0, 730, n_opp)]

    opps = pd.DataFrame({
        "opp_id":       [f"OPP{i:05d}" for i in range(n_opp)],
        "account_id":   rng.choice(accounts["account_id"], n_opp),
        "opp_name":     [f"Deal_{i}" for i in range(n_opp)],
        "stage":        rng.choice(stages, n_opp, p=stage_probs),
        "amount":       np.round(rng.uniform(5_000, 500_000, n_opp), -2),
        "probability":  rng.integers(10, 100, n_opp),
        "close_date":   [d.strftime("%Y-%m-%d") for d in close_dates],
        "owner":        rng.choice(owners, n_opp),
        "product_line": rng.choice(products, n_opp),
    })

    return accounts, opps


# ─────────────────────────────────────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────────────────────────────────────

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA, "r") as f:
        sql = f.read()
    # SQLite ne supporte pas toutes les syntaxes PostgreSQL — adapter
    sql = sql.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
    sql = sql.replace("NUMERIC(15,2)", "REAL")
    sql = sql.replace("NUMERIC(5,2)", "REAL")
    sql = sql.replace("VARCHAR(50)", "TEXT")
    sql = sql.replace("VARCHAR(100)", "TEXT")
    sql = sql.replace("VARCHAR(200)", "TEXT")
    sql = sql.replace("VARCHAR(300)", "TEXT")
    sql = sql.replace("VARCHAR(20)", "TEXT")
    sql = sql.replace("VARCHAR(30)", "TEXT")
    sql = sql.replace("TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "TEXT DEFAULT CURRENT_TIMESTAMP")
    # Exécuter chaque statement séparément
    for stmt in sql.split(";"):
        stmt = stmt.strip()
        if stmt:
            try:
                conn.execute(stmt)
            except Exception as e:
                pass
    conn.commit()
    conn.close()
    print("[DB] Initialisée.")


def load_data():
    accounts, opps = generate_crm_data()
    conn = sqlite3.connect(DB_PATH)
    accounts.to_sql("accounts", conn, if_exists="replace", index=False)
    opps.to_sql("opportunities", conn, if_exists="replace", index=False)
    conn.close()
    print(f"[ETL] {len(accounts)} comptes, {len(opps)} opportunités chargés.")


def get_kpis() -> dict:
    conn = sqlite3.connect(DB_PATH)
    opps = pd.read_sql("SELECT * FROM opportunities", conn)
    conn.close()

    total_pipeline = opps[~opps["stage"].isin(["Closed Won","Closed Lost"])]["amount"].sum()
    won            = opps[opps["stage"] == "Closed Won"]
    lost           = opps[opps["stage"] == "Closed Lost"]
    closed         = pd.concat([won, lost])
    win_rate       = len(won) / len(closed) * 100 if len(closed) > 0 else 0

    return {
        "total_revenue":    won["amount"].sum(),
        "pipeline_value":   total_pipeline,
        "win_rate":         win_rate,
        "avg_deal_size":    won["amount"].mean() if len(won) > 0 else 0,
        "total_deals":      len(opps),
        "won_deals":        len(won),
        "lost_deals":       len(lost),
    }


if __name__ == "__main__":
    import sys
    init_db()
    load_data()
    kpis = get_kpis()
    print("\n📊 KPIs:")
    for k, v in kpis.items():
        print(f"  {k:20s}: {v:,.2f}" if isinstance(v, float) else f"  {k:20s}: {v}")