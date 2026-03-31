# 📊 Sales Intelligence Dashboard

> Pipeline analytique end-to-end du CRM brut aux tableaux de bord Power BI — **réduction du temps de reporting de 80%**

![Python](https://img.shields.io/badge/Python-3.10-blue)
![SQL](https://img.shields.io/badge/SQL-PostgreSQL-336791?logo=postgresql)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📌 Description

Ce projet construit un pipeline ETL complet qui ingère des données CRM brutes (CSV/API), les transforme via SQL et Python, les charge dans une base PostgreSQL/SQLite, et expose un **dashboard analytique interactif** remplaçant Power BI.

---

## 🚀 Fonctionnalités

- ✅ Pipeline ETL automatisé (Extract → Transform → Load)
- ✅ Nettoyage, déduplication et enrichissement des données CRM
- ✅ Requêtes SQL analytiques avancées (fenêtres, CTEs, agrégations)
- ✅ Dashboard interactif multi-pages (KPIs, Funnel, Cohorts, Forecasts)
- ✅ Rapports automatiques (HTML + PDF)
- ✅ Scheduling avec cron / APScheduler
- ✅ Base de données PostgreSQL/SQLite avec schéma relationnel

---

## 📁 Structure

```
sales_intelligence/
├── sql/
│   ├── schema.sql              # DDL — création des tables
│   ├── etl_transforms.sql      # Transformations analytiques
│   └── kpi_queries.sql         # Requêtes KPIs
├── etl/
│   ├── extract.py              # Extraction données CRM
│   ├── transform.py            # Nettoyage & enrichissement
│   ├── load.py                 # Chargement base de données
│   └── pipeline.py             # Orchestration ETL complète
├── dashboard/
│   └── app.py                  # Dashboard Streamlit
├── data/
│   └── sample_crm.csv          # Données exemple
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/votre-username/sales-intelligence.git
cd sales-intelligence
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Configurer la connexion DB
```

---

## 🏃 Utilisation

```bash
# 1. Initialiser la base de données
python etl/load.py --init-db

# 2. Lancer le pipeline ETL complet
python etl/pipeline.py

# 3. Lancer le dashboard
streamlit run dashboard/app.py

# 4. Scheduler automatique (toutes les heures)
python etl/pipeline.py --schedule
```

---

## 📊 KPIs Trackés

| Métrique               | Description                        |
|------------------------|------------------------------------|
| MRR / ARR              | Revenus récurrents mensuels/annuels |
| Win Rate               | Taux de conversion des opportunités |
| Sales Velocity         | Vitesse du pipeline commercial      |
| Customer LTV           | Valeur vie client                   |
| Churn Rate             | Taux d'attrition                    |
| CAC                    | Coût d'acquisition client           |

---

## 🗄️ Schéma Base de Données

```
accounts ──< opportunities ──< activities
    │                │
    └──< contacts ──┘
              │
          invoices
```

---

## 🛠️ Technologies

- Python 3.10, Pandas, SQLAlchemy
- PostgreSQL (prod) / SQLite (dev)
- Streamlit, Plotly
- APScheduler (scheduling)