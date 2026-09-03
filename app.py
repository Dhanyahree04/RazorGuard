
import streamlit as st
import pandas as pd
import numpy as np


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="RazorGuard",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        "razorguard_dashboard_data.csv"
    )

    audit = pd.read_csv(
        "razorguard_audit_log.csv"
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    return df, audit


df, audit = load_data()


VERIFY_THRESHOLD = 0.15
ESCALATE_THRESHOLD = 0.90


# ============================================================
# HEADER
# ============================================================

st.title("🛡️ RazorGuard")

st.subheader(
    "Cost-Aware Fraud Spike Detector"
)

st.caption(
    "Detect abnormal payment behaviour, explain risk, "
    "and route transactions to ALLOW, VERIFY, or ESCALATE."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "Risk Policy"
)

st.sidebar.metric(
    "VERIFY Threshold",
    f"{VERIFY_THRESHOLD:.2f}"
)

st.sidebar.metric(
    "ESCALATE Threshold",
    f"{ESCALATE_THRESHOLD:.2f}"
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "ESCALATE means manual/secondary review — "
    "not autonomous blocking."
)


# ============================================================
# CALCULATE KPIs
# ============================================================

total_txns = len(df)

fraud_mask = (
    df["actual_label"] == 1
)

legit_mask = (
    df["actual_label"] == 0
)


total_fraud = int(
    fraud_mask.sum()
)


fraud_intervened = int(
    (
        fraud_mask
        &
        (df["decision"] != "ALLOW")
    ).sum()
)


fraud_missed = int(
    (
        fraud_mask
        &
        (df["decision"] == "ALLOW")
    ).sum()
)


intervention_rate = (
    fraud_intervened
    /
    total_fraud
    *
    100
    if total_fraud > 0
    else 0
)


total_fraud_value = (
    df.loc[
        fraud_mask,
        "amount"
    ].sum()
)


missed_fraud_value = (
    df.loc[
        fraud_mask
        &
        (df["decision"] == "ALLOW"),
        "amount"
    ].sum()
)


protected_fraud_value = (
    total_fraud_value
    -
    missed_fraud_value
)


protected_value_pct = (
    protected_fraud_value
    /
    total_fraud_value
    *
    100
    if total_fraud_value > 0
    else 0
)


# ============================================================
# LEGITIMATE CUSTOMER FRICTION
# ============================================================

total_legit = int(
    legit_mask.sum()
)

legit_intervened = int(
    (
        legit_mask
        &
        (df["decision"] != "ALLOW")
    ).sum()
)

legit_friction_rate = (
    legit_intervened
    /
    total_legit
    *
    100
    if total_legit > 0
    else 0
)


# ============================================================
# KPI ROW
# ============================================================

st.markdown("## Performance Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Transactions",
    f"{total_txns:,}"
)

c2.metric(
    "Fraud Transactions",
    f"{total_fraud:,}"
)

c3.metric(
    "Fraud Intervention Rate",
    f"{intervention_rate:.1f}%"
)

c4.metric(
    "Protected Fraud Value",
    f"₹{protected_fraud_value:,.0f}"
)


c5, c6, c7, c8, c9 = st.columns(5)

c5.metric(
    "Fraud Missed",
    fraud_missed
)

c6.metric(
    "Missed Fraud Value",
    f"₹{missed_fraud_value:,.0f}"
)

c7.metric(
    "Protected Value %",
    f"{protected_value_pct:.1f}%"
)

c8.metric(
    "Legitimate Friction Rate",
    f"{legit_friction_rate:.1f}%"
)

c9.metric(
    "Manual Reviews",
    int(
        (
            df["decision"]
            ==
            "ESCALATE"
        ).sum()
    )
)


# ============================================================
# DECISION DISTRIBUTION
# ============================================================

st.markdown("---")
st.markdown("## Risk Routing")

left, right = st.columns(2)


with left:

    st.markdown(
        "### ALLOW / VERIFY / ESCALATE"
    )

    decision_counts = (
        df["decision"]
        .value_counts()
        .reindex(
            [
                "ALLOW",
                "VERIFY",
                "ESCALATE"
            ],
            fill_value=0
        )
    )

    st.bar_chart(
        decision_counts
    )


with right:

    st.markdown(
        "### Fraud Concentration by Queue"
    )

    queue_fraud_rate = (
        df.groupby(
            "decision"
        )["actual_label"]
        .mean()
        .reindex(
            [
                "ALLOW",
                "VERIFY",
                "ESCALATE"
            ]
        )
        .fillna(0)
        * 100
    )

    st.bar_chart(
        queue_fraud_rate
    )

    st.caption(
        "Higher fraud concentration in ESCALATE "
        "indicates effective risk prioritisation."
    )


# ============================================================
# DECISION TABLE
# ============================================================

st.markdown("### Routing Matrix")

routing_matrix = pd.crosstab(
    df["decision"],
    df["actual_label"]
)

routing_matrix = routing_matrix.rename(
    columns={
        0: "Legitimate",
        1: "Fraud"
    }
)

st.dataframe(
    routing_matrix,
    use_container_width=True
)


# ============================================================
# MANUAL REVIEW QUEUE
# ============================================================

st.markdown("---")
st.markdown("## 🚨 Manual Review Queue")


manual_queue = (
    df[
        df["decision"]
        ==
        "ESCALATE"
    ]
    .sort_values(
        "risk_score",
        ascending=False
    )
)


st.caption(
    f"{len(manual_queue)} transactions "
    "currently routed for high-confidence review."
)


review_cols = [
    "transaction_id",
    "timestamp",
    "merchant_id",
    "amount",
    "risk_score",
    "reason_codes",
    "review_state"
]


st.dataframe(
    manual_queue[
        review_cols
    ],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# TRANSACTION INSPECTOR
# ============================================================

st.markdown("---")
st.markdown("## 🔍 Transaction Inspector")


txn_ids = (
    df[
        "transaction_id"
    ].tolist()
)


selected_txn = st.selectbox(
    "Select Transaction",
    txn_ids
)


txn = (
    df[
        df["transaction_id"]
        ==
        selected_txn
    ]
    .iloc[0]
)


a, b, c, d = st.columns(4)


a.metric(
    "Risk Score",
    f"{txn['risk_score']:.4f}"
)

b.metric(
    "Decision",
    txn["decision"]
)

c.metric(
    "Amount",
    f"₹{txn['amount']:,.2f}"
)

d.metric(
    "Review State",
    txn["review_state"]
)


st.markdown(
    "### Behavioural Reason Codes"
)

st.info(
    txn["reason_codes"]
)


# ============================================================
# BEHAVIOURAL FEATURES
# ============================================================

st.markdown(
    "### Behavioural Signals"
)


signal_data = pd.DataFrame({

    "Signal": [
        "Amount Z-score",
        "New Device",
        "IP Txns — Previous 10 min",
        "Customer Txns — Previous 10 min",
        "Failed Attempts — Previous 1 hour",
        "Country Mismatch"
    ],

    "Value": [
        round(
            txn["amount_zscore_past"],
            3
        ),

        int(
            txn["is_new_device"]
        ),

        int(
            txn["ip_txn_count_10min_past"]
        ),

        int(
            txn["customer_txn_count_10min_past"]
        ),

        int(
            txn[
                "customer_failed_attempts_1h_past"
            ]
        ),

        int(
            txn["country_mismatch"]
        )
    ]
})


st.dataframe(
    signal_data,
    use_container_width=True,
    hide_index=True
)


st.caption(
    "Reason codes describe observable behavioural indicators. "
    "They are not presented as exact causal explanations "
    "of the XGBoost model."
)


# ============================================================
# FILTERABLE TRANSACTION EXPLORER
# ============================================================

st.markdown("---")
st.markdown("## Transaction Explorer")


selected_decisions = st.multiselect(
    "Decision",
    [
        "ALLOW",
        "VERIFY",
        "ESCALATE"
    ],
    default=[
        "ALLOW",
        "VERIFY",
        "ESCALATE"
    ]
)


min_risk = st.slider(
    "Minimum Risk Score",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.05
)


filtered_df = df[
    (
        df["decision"]
        .isin(
            selected_decisions
        )
    )
    &
    (
        df["risk_score"]
        >= min_risk
    )
]


st.write(
    f"Showing {len(filtered_df):,} transactions"
)


st.dataframe(
    filtered_df[
        [
            "transaction_id",
            "timestamp",
            "merchant_id",
            "amount",
            "risk_score",
            "decision",
            "reason_codes"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# AUDIT LOG
# ============================================================

st.markdown("---")
st.markdown("## 📋 Audit Trail")


st.dataframe(
    audit.head(100),
    use_container_width=True,
    hide_index=True
)


audit_csv = audit.to_csv(
    index=False
).encode(
    "utf-8"
)


st.download_button(
    label="Download Audit Log",
    data=audit_csv,
    file_name="razorguard_audit_log.csv",
    mime="text/csv"
)


# ============================================================
# METHODOLOGY
# ============================================================

st.markdown("---")
st.markdown("## Methodology")


st.markdown(
    """
**Risk model:** XGBoost binary fraud classifier

**Evaluation:** Chronological train / validation / held-out test split

**Feature design:** Historical features use only information available before each transaction

**VERIFY:** Step-up authentication / additional verification

**ESCALATE:** High-confidence transaction routed for manual or secondary review

**Cost-aware policy:** Thresholds selected using missed-fraud value and assumed customer-friction / review costs.

The ₹15 VERIFY and ₹150 ESCALATE costs are transparent modelling assumptions, not claimed Razorpay internal costs.
"""
)
