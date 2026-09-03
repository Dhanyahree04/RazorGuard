# RazorGuard — Cost-Aware Fraud Spike Detector

RazorGuard is a defense-only payment fraud risk management prototype.

It assigns a fraud risk score and routes transactions into:

- ALLOW — low-risk transaction
- VERIFY — step-up verification
- ESCALATE — high-confidence transaction routed for manual review

## Final Risk Policy

- VERIFY threshold: 0.15
- ESCALATE threshold: 0.90

## Held-Out Test Results

- Fraud intervention rate: 89.2%
- Protected fraud value: 92.1%
- Legitimate friction rate: 12.0%

## Methodology

- XGBoost fraud classifier
- Chronological train / validation / test split
- Leakage-safe historical behavioural features
- Cost-aware threshold selection
- Transaction-level behavioural reason codes
- Auditable ALLOW / VERIFY / ESCALATE decisions

The ₹15 VERIFY cost and ₹150 ESCALATE cost are transparent modelling assumptions and are not claimed Razorpay internal costs.

ESCALATE means manual or secondary review, not autonomous blocking.
