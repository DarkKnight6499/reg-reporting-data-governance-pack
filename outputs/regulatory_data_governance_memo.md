# SYNTHETIC Regulatory Data Governance Demonstration

## Page 1: Portfolio, quality and reserve

Reporting snapshot: 2024-09-30.
Audience: portfolio reviewers. Status: educational demonstration, no filing or operational sign-off.

All facilities, parameters, ledger entries and issue histories are SYNTHETIC.
This memo uses generated CSV results. It provides no conclusion about any bank's financial health or regulatory compliance.

### Portfolio and data quality

The tape contains 5,000 facilities and 2,787 observed borrowers,
with $26,452,761,336.01 committed and $18,779,563,345.31 drawn.
The illustrative 18-field schedule ties to tape commitment, drawn and collateral totals within one cent.
The 18 clean-tape rules report 0 failed rule evaluations.
The defect benchmark reports 200 failed rule evaluations over 150 injected defective facilities.
Record-level tests compare flagged facility IDs with the injected set, including false-positive checks.

| dq_rule_id | fail_count | pass_rate_pct |
| :--- | :--- | :--- |
| DQ_COMP_01 | 20 | 99.6 |
| DQ_COMP_02 | 30 | 99.4 |
| DQ_COMP_03 | 0 | 100.0 |
| DQ_VAL_01 | 0 | 100.0 |
| DQ_VAL_02 | 0 | 100.0 |
| DQ_RSN_01 | 25 | 99.5 |
| DQ_VAL_03 | 25 | 99.5 |
| DQ_RSN_02 | 25 | 99.5 |
| DQ_RSN_03 | 25 | 99.5 |
| DQ_REF_01 | 0 | 100.0 |
| DQ_VAL_04 | 0 | 100.0 |
| DQ_VAL_05 | 0 | 100.0 |
| DQ_RSN_04 | 25 | 99.5 |
| DQ_VAL_06 | 25 | 99.5 |
| DQ_VAL_07 | 0 | 100.0 |
| DQ_RSN_05 | 0 | 100.0 |
| DQ_VAL_08 | 0 | 100.0 |
| DQ_VAL_09 | 0 | 100.0 |

All 18 schedule fields have owner, definition, CDE flag and actual local lineage in the catalog.
Every schedule field maps to at least one automated DQ rule; coverage remains limited to configured checks.
Synthetic issue ages are generated per injected facility; they are not measured remediation performance.
The 12 synthetic closed examples average 37.42 days to close.

### Illustrative credit loss allowance

Annual rating PD is compounded over remaining contractual tenor: lifetime PD = 1 - (1 - annual PD)^years.
EAD = drawn + undrawn x configured product CCF. Base loss = EAD x lifetime PD x collateral LGD.
Overlay adds 3% of base loss, plus 15% for CRE and 10% for ratings 6 to 8.
These are assumed rates, not estimated forecasts or approved policy.

Base reserve is $788,641,963.52; overlay is $95,238,474.08; ending allowance is $883,880,437.60.
Coverage on drawn balance is 4.71%.
Beginning allowance $833,057,312.44 + provision $61,123,125.16
minus gross charge-offs $12,450,000.00 + recoveries $2,150,000.00 = ending allowance.
Provision is a balancing amount. Base and overlay are ending-stock disclosures, not components of current provision.

<div style="page-break-after: always;"></div>

## Page 2: Reconciliation, issue aging and limitations

### Synthetic liquidity report versus ledger

Active breaks require absolute variance above $10,000 OR relative variance above
0.05%, after clearing variances at or below $100.
Relative variance uses absolute GL balance; a nonzero variance against zero GL has infinite relative variance.

| recon_id | variance_amount | root_cause_tag | break_age_days |
| :--- | :--- | :--- | :--- |
| REC_001 | 2450000.0 | Cutoff Timing Mismatch | 3 |
| REC_002 | -420000.0 | Manual Journal Entry | 21 |
| REC_003 | 850000.0 | Unmapped Facility Product Code | 38 |
| REC_004 | -185000.0 | Synthetic Valuation Adjustment | 9 |

There are 4 active breaks, gross absolute variance $3,905,000.00,
net variance $2,695,000.00, and 1 older than 30 days.
Signs use schedule minus GL. Root causes are assigned synthetic scenario labels, not inferred diagnoses.
The report combines selected drawn and commitment proxies with a fee residual; it is not a complete liquidity outflow calculation.
Term undrawn amounts are outside this selected reconciliation scope.

### Synthetic open issue inventory

| age_bucket | open_issues_count | avg_age_days |
| :--- | :--- | :--- |
| 0-30 Days | 38 | 20.13 |
| 31-60 Days | 25 | 44.36 |
| 61-90 Days | 33 | 76.91 |
| 91+ Days | 54 | 116.56 |

The inventory links each open issue to an injected facility. Closed examples are a separate assumed history.
The closed-history count appears in the historical summary row under the shared count column.

### Checklist and next steps

The illustrative principles 1 to 11 checklist averages 1.09/3 on a project-defined evidence scale.
It does not certify BCBS 239 compliance. No board approval, production monitoring, secure distribution or institutional policy evidence exists.

Priorities: extend rules to uncaptured fields; use independently maintained reference masters; validate credit parameters;
add controlled distribution and operational monitoring before considering a production implementation.
No remediation action has been executed or scheduled by this project.

### Limits

The schedule and liquidity report are simplified style examples, not official submission schemas.
LEIs are fabricated strings without checksum validation. Credit losses omit amortization, prepayment,
scenario forecasts, discounting and separate funded versus unfunded reserve treatment.
A single seeded snapshot cannot establish real performance or compliance.
This Markdown has one explicit page break; physical pagination depends on the renderer and paper settings.
