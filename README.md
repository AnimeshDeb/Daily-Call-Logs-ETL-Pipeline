# Automated Operational Analytics Pipeline
### **End-to-End Data Engineering & Visualization Project**

## Executive Summary
This project demonstrates a fully automated **ETL (Extract, Transform, Load)** pipeline designed to simulate a live call center environment. Instead of relying on a static, "dead" dataset, I engineered a system that regenerates "live" operational data every 24 hours. This provides a real-time look at Call Center performance, Service Level Agreement (SLA) compliance, and agent efficiency without any manual intervention.



## The Tech Stack
* **Language:** Python 3.11 (Environment managed via `pyenv`)
* **Libraries:** `Pandas` (Data Manipulation), `Supabase-py` (Database Connection), `python-dotenv`
* **Database:** PostgreSQL (Cloud-hosted on **Supabase**)
* **Automation:** **GitHub Actions** (CI/CD Cron Jobs)
* **Visualization:** **Tableau Desktop** (Live PostgreSQL Connection)

## Infrastructure Architecture
1.  **Extraction:** A Python script extracts a random sample of 150 records daily from a historical Call Centre Simulation dataset to simulate fluctuating daily volume.
2.  **Transformation:**
    * **Data Integrity:** Generates unique `UUID` identifiers for every transaction to ensure primary key constraints in Postgres.
    * **Time-Series Simulation:** Overwrites historical timestamps with the **current date** to simulate live daily activity.
    * **Logic Layer:** Calculates real-time **SLA Breach** flags (Boolean) based on a 60-second wait time threshold.
3.  **Loading:** Transformed data is securely pushed into a cloud-hosted PostgreSQL database using GitHub Secrets and the Supabase Service Role.
4.  **Automation:** A GitHub Actions workflow triggers the script daily at **00:00 UTC**, ensuring the analytics dashboard updates automatically every morning.

## Key Business Metrics Tracked
* **Average Handle Time (AHT):** Monitoring the total duration of agent-customer interactions to optimize staffing.
* **SLA Compliance %:** Tracking the percentage of calls answered within the 60-second target to maintain service quality.
* **Call Volume Trends:** Visualizing peak hours and categorical demand to identify resource bottlenecks.

## Security & Best Practices
* **Environment Variables:** Utilized `.env` files and GitHub Encrypted Secrets to protect database credentials.
* **Modular Code:** Built the ETL process using functional programming blocks for scalability and error handling.
* **Virtual Environments:** Used `pyenv` and `venv` to ensure a clean, reproducible dependency tree.

---
*Developed by Animesh Deb — Data Analyst & Engineering Enthusiast*
