# 🛡️ RazorGuard — Cost-Aware Fraud Spike Detector

RazorGuard is a defense-only payment fraud risk management prototype designed to detect suspicious transaction behaviour, estimate fraud risk, and route each transaction into one of three operational actions:

- **ALLOW** — low-risk transaction
- **VERIFY** — step-up verification for uncertain transactions
- **ESCALATE** — high-confidence transaction routed for manual or secondary review

## 🚀 Live Demo

**Streamlit App:**  
https://razorguard-xjumezmmzk32cbebawz2hu.streamlit.app

---

## 🎯 Problem

Fraud detection is not only about catching fraudulent payments.

An overly aggressive system can also hurt legitimate customers through unnecessary verification or manual review.

RazorGuard therefore focuses on balancing:

- fraud detection,
- customer friction,
- operational review load,
- and monetary loss.

---

## 🧠 Approach

RazorGuard uses an **XGBoost binary fraud classifier** trained on leakage-safe behavioural features.

The pipeline includes:

1. Synthetic behavioural transaction generation
2. Hard legitimate and subtle fraud scenarios
3. Past-only feature engineering
4. Chronological train / validation / test split
5. XGBoost fraud-risk scoring
6. Cost-aware threshold selection
7. ALLOW / VERIFY / ESCALATE routing
8. Behavioural reason codes
9. Audit logging
10. Streamlit risk-management dashboard

---

## 🔒 Leakage-Safe Feature Engineering

Historical features are calculated using only information available **before the current transaction**.

Examples include:

- merchant historical amount mean and standard deviation
- amount z-score relative to past merchant behaviour
- previous device usage
- IP transaction velocity
- customer transaction velocity
- recent failed payment attempts
- country mismatch

A dedicated regression test recomputes features on a historical prefix and verifies that future transactions do not change past feature values.

---

## ⏱️ Evaluation Strategy

The dataset is split chronologically:

**Train → Validation → Held-Out Test**

This better represents a real fraud-detection setting than a random split.

The validation set is used for threshold selection.

The held-out test set is evaluated only after the operating thresholds are locked.

---

## ⚖️ Cost-Aware Risk Policy

Final operating thresholds:

| Risk Score | Action |
|---|---|
| `< 0.15` | ALLOW |
| `0.15 – < 0.90` | VERIFY |
| `≥ 0.90` | ESCALATE |

Thresholds were selected using a validation-time cost model that considers:

- actual transaction value for missed fraud,
- **₹15** assumed friction cost for unnecessary VERIFY,
- **₹150** assumed operational/customer-friction cost for unnecessary ESCALATE.

These are transparent modelling assumptions and are **not claimed Razorpay internal costs**.

The purely lowest-cost threshold was not selected mechanically because it produced excessive legitimate-customer verification. The final policy balances fraud protection with operational and customer-experience impact.

---

## 📊 Held-Out Test Results

| Metric | Result |
|---|---:|
| Transactions | 1,736 |
| Fraud Transactions | 157 |
| Fraud Routed for Intervention | 89.2% |
| Protected Fraud Value | ₹681,334 |
| Protected Fraud Value % | 92.1% |
| Fraud Missed | 17 |
| Missed Fraud Value | ₹58,185 |
| Legitimate Friction Rate | 12.0% |
| Manual Review Queue | 112 |

### Key takeaway

> **RazorGuard protected 92.1% of fraudulent transaction value while limiting legitimate-customer intervention to 12.0%.**

---

## 🔍 Explainability

Each transaction is accompanied by transparent behavioural reason codes such as:

- elevated amount relative to merchant history,
- previously unseen device,
- high IP transaction velocity,
- recent failed payment attempts,
- country mismatch.

These reason codes describe observable behavioural indicators and are **not presented as exact causal explanations of the XGBoost model**.

---

## 📋 Auditability

RazorGuard maintains an audit trail containing:

- transaction ID
- timestamp
- merchant and customer identifiers
- transaction amount
- risk score
- decision
- behavioural reason codes
- review state
- offline evaluation label

In a production environment, the true fraud label would arrive later through confirmed fraud or chargeback outcomes.

---

## 🖥️ Dashboard

The Streamlit dashboard provides:

- performance KPIs
- ALLOW / VERIFY / ESCALATE distribution
- fraud concentration by queue
- high-confidence manual review queue
- transaction-level risk inspection
- behavioural reason codes
- filterable transaction explorer
- downloadable audit log

---

## 🛡️ Defense-Only Design

RazorGuard is designed strictly for defensive fraud-risk management.

**ESCALATE does not autonomously block a transaction.**

It routes high-confidence cases for manual or secondary review.

---

## 🧰 Tech Stack

- Python
- Pandas
- NumPy
- XGBoost
- Scikit-learn
- Streamlit
- GitHub
- Streamlit Community Cloud

---
## 📁 Deployment Repository

```text
RazorGuard/
├── app.py
├── razorguard_dashboard_data.csv
├── razorguard_audit_log.csv
├── architecture_diagram.png
├── requirements.txt
└── README.md

![RazorGuard Architecture](architecture_diagram.png)
