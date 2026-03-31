-- ============================================================
-- schema.sql — Schéma relationnel Sales Intelligence
-- Compatible PostgreSQL & SQLite
-- ============================================================

-- Comptes / Entreprises clients
CREATE TABLE IF NOT EXISTS accounts (
    id              SERIAL PRIMARY KEY,
    account_id      VARCHAR(50)  UNIQUE NOT NULL,
    company_name    VARCHAR(200) NOT NULL,
    industry        VARCHAR(100),
    country         VARCHAR(100),
    region          VARCHAR(100),
    employee_count  INTEGER,
    annual_revenue  NUMERIC(15,2),
    account_tier    VARCHAR(20) CHECK (account_tier IN ('Enterprise','Mid-Market','SMB')),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contacts
CREATE TABLE IF NOT EXISTS contacts (
    id              SERIAL PRIMARY KEY,
    contact_id      VARCHAR(50) UNIQUE NOT NULL,
    account_id      VARCHAR(50) REFERENCES accounts(account_id),
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    email           VARCHAR(200),
    title           VARCHAR(100),
    phone           VARCHAR(50),
    lead_source     VARCHAR(100),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Opportunités commerciales
CREATE TABLE IF NOT EXISTS opportunities (
    id              SERIAL PRIMARY KEY,
    opp_id          VARCHAR(50) UNIQUE NOT NULL,
    account_id      VARCHAR(50) REFERENCES accounts(account_id),
    contact_id      VARCHAR(50) REFERENCES contacts(contact_id),
    opp_name        VARCHAR(200),
    stage           VARCHAR(50) CHECK (stage IN (
                        'Prospecting','Qualification','Proposal',
                        'Negotiation','Closed Won','Closed Lost')),
    amount          NUMERIC(15,2),
    probability     NUMERIC(5,2),
    close_date      DATE,
    owner           VARCHAR(100),
    product_line    VARCHAR(100),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Activités (appels, emails, réunions)
CREATE TABLE IF NOT EXISTS activities (
    id              SERIAL PRIMARY KEY,
    activity_id     VARCHAR(50) UNIQUE NOT NULL,
    opp_id          VARCHAR(50) REFERENCES opportunities(opp_id),
    contact_id      VARCHAR(50) REFERENCES contacts(contact_id),
    activity_type   VARCHAR(50) CHECK (activity_type IN ('Call','Email','Meeting','Demo','Proposal Sent')),
    subject         VARCHAR(300),
    outcome         VARCHAR(50),
    activity_date   TIMESTAMP,
    duration_min    INTEGER,
    created_by      VARCHAR(100)
);

-- Factures
CREATE TABLE IF NOT EXISTS invoices (
    id              SERIAL PRIMARY KEY,
    invoice_id      VARCHAR(50) UNIQUE NOT NULL,
    account_id      VARCHAR(50) REFERENCES accounts(account_id),
    opp_id          VARCHAR(50) REFERENCES opportunities(opp_id),
    invoice_date    DATE,
    due_date        DATE,
    amount          NUMERIC(15,2),
    paid_amount     NUMERIC(15,2) DEFAULT 0,
    status          VARCHAR(30) CHECK (status IN ('Draft','Sent','Paid','Overdue','Cancelled')),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vue analytique : KPIs par période
CREATE VIEW IF NOT EXISTS v_monthly_kpis AS
SELECT
    strftime('%Y-%m', close_date)            AS month,
    COUNT(*)                                  AS total_deals,
    SUM(CASE WHEN stage='Closed Won' THEN 1 ELSE 0 END) AS won_deals,
    SUM(CASE WHEN stage='Closed Lost' THEN 1 ELSE 0 END) AS lost_deals,
    ROUND(100.0 * SUM(CASE WHEN stage='Closed Won' THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_rate,
    SUM(CASE WHEN stage='Closed Won' THEN amount ELSE 0 END) AS revenue_won,
    AVG(amount) AS avg_deal_size
FROM opportunities
WHERE close_date IS NOT NULL
GROUP BY strftime('%Y-%m', close_date);

-- Vue pipeline funnel
CREATE VIEW IF NOT EXISTS v_pipeline_funnel AS
SELECT
    stage,
    COUNT(*)       AS deal_count,
    SUM(amount)    AS total_value,
    AVG(amount)    AS avg_value,
    AVG(probability) AS avg_probability
FROM opportunities
GROUP BY stage
ORDER BY
    CASE stage
        WHEN 'Prospecting'   THEN 1
        WHEN 'Qualification' THEN 2
        WHEN 'Proposal'      THEN 3
        WHEN 'Negotiation'   THEN 4
        WHEN 'Closed Won'    THEN 5
        WHEN 'Closed Lost'   THEN 6
    END;