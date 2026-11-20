import os
import sys
import pandas as pd

# CONFIG
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT) if REPO_ROOT not in sys.path else None
from python.config import *
MEMO_TITLE = "SYNTHETIC Regulatory Data Governance Demonstration"

def markdown_table(df):
    headers = list(df.columns)
    rows = ["| " + " | ".join(headers) + " |", "| " + " | ".join(":---" for _ in headers) + " |"]
    for record in df.to_dict("records"):
        rows.append("| " + " | ".join(str(record[column]) for column in headers) + " |")
    return "\n".join(rows)

def build_executive_memo():
    tape = pd.read_csv(LOAN_TAPE_CLEAN_PATH)
    inputs = pd.read_csv(CECL_FACILITY_PATH)
    roll = pd.read_csv(CECL_ROLL_FORWARD_PATH)
    dq = pd.read_csv(DQ_RESULTS_PATH)
    clean = pd.read_csv(DQ_CLEAN_RESULTS_PATH)
    aging = pd.read_csv(DQ_AGING_PATH)
    recon = pd.read_csv(RECON_BREAKS_PATH)
    bcbs = pd.read_csv(BCBS_ASSESSMENT_PATH)
    active = recon.loc[recon[COL_BREAK_FLAG].eq("Active Break")]
    ending = inputs[COL_TOTAL_RESERVE].sum()
    base = inputs[COL_BASE_LIFETIME_LOSS].sum()
    overlay = inputs[COL_QUALITATIVE_OVERLAY].sum()
    amount = lambda label: roll.loc[roll[COL_COMPONENT].eq(label), COL_AMOUNT].item()
    closed = pd.read_csv(DQ_CLOSED_PATH)
    memo = f"""# {MEMO_TITLE}

## Page 1: Portfolio, quality and reserve

Reporting snapshot: {REPORTING_DATE}.
Audience: portfolio reviewers. Status: educational demonstration, no filing or operational sign-off.

All facilities, parameters, ledger entries and issue histories are SYNTHETIC.
This memo uses generated CSV results. It provides no conclusion about any bank's financial health or regulatory compliance.

### Portfolio and data quality

The tape contains {len(tape):,} facilities and {tape[COL_BORROWER_ID].nunique():,} observed borrowers,
with ${tape[COL_COMMITTED_EXPOSURE].sum():,.2f} committed and ${tape[COL_DRAWN_BALANCE].sum():,.2f} drawn.
The illustrative 18-field schedule ties to tape commitment, drawn and collateral totals within one cent.
The 18 clean-tape rules report {int(clean[COL_FAIL_COUNT].sum())} failed rule evaluations.
The defect benchmark reports {int(dq[COL_FAIL_COUNT].sum())} failed rule evaluations over 150 injected defective facilities.
Record-level tests compare flagged facility IDs with the injected set, including false-positive checks.

{markdown_table(dq[[COL_DQ_RULE_ID, COL_FAIL_COUNT, COL_PASS_RATE_PCT]])}

All 18 schedule fields have owner, definition, CDE flag and actual local lineage in the catalog.
Every schedule field maps to at least one automated DQ rule; coverage remains limited to configured checks.
Synthetic issue ages are generated per injected facility; they are not measured remediation performance.
The {len(closed)} synthetic closed examples average {closed[COL_CLOSE_DAYS].mean():.2f} days to close.

### Illustrative credit loss allowance

Annual rating PD is compounded over remaining contractual tenor: lifetime PD = 1 - (1 - annual PD)^years.
EAD = drawn + undrawn x configured product CCF. Base loss = EAD x lifetime PD x collateral LGD.
Overlay adds {OVERLAY_BASE:.0%} of base loss, plus {OVERLAY_CRE:.0%} for CRE and {OVERLAY_CRITICIZED:.0%} for ratings 6 to 8.
These are assumed rates, not estimated forecasts or approved policy.

Base reserve is ${base:,.2f}; overlay is ${overlay:,.2f}; ending allowance is ${ending:,.2f}.
Coverage on drawn balance is {ending / tape[COL_DRAWN_BALANCE].sum() * 100:.2f}%.
Beginning allowance ${amount('Beginning Allowance'):,.2f} + provision ${amount('Provision Expense'):,.2f}
minus gross charge-offs ${GROSS_CHARGE_OFFS:,.2f} + recoveries ${RECOVERIES:,.2f} = ending allowance.
Provision is a balancing amount. Base and overlay are ending-stock disclosures, not components of current provision.

{MEMO_PAGE_BREAK}

## Page 2: Reconciliation, issue aging and limitations

### Synthetic liquidity report versus ledger

Active breaks require absolute variance above ${RECON_TOLERANCE_DOLLARS:,.0f} OR relative variance above
{RECON_TOLERANCE_PCT:.2%}, after clearing variances at or below ${RECON_IMMATERIAL_THRESHOLD:,.0f}.
Relative variance uses absolute GL balance; a nonzero variance against zero GL has infinite relative variance.

{markdown_table(active[[COL_RECON_ID, COL_VARIANCE_AMOUNT, COL_ROOT_CAUSE_TAG, COL_BREAK_AGE_DAYS]])}

There are {len(active)} active breaks, gross absolute variance ${active[COL_VARIANCE_AMOUNT].abs().sum():,.2f},
net variance ${active[COL_VARIANCE_AMOUNT].sum():,.2f}, and {int(active[COL_BREAK_AGE_DAYS].gt(RECON_AGE_LIMITS[2]).sum())} older than 30 days.
Signs use schedule minus GL. Root causes are assigned synthetic scenario labels, not inferred diagnoses.
The report combines selected drawn and commitment proxies with a fee residual; it is not a complete liquidity outflow calculation.
Term undrawn amounts are outside this selected reconciliation scope.

### Synthetic open issue inventory

{markdown_table(aging[[COL_AGE_BUCKET, COL_OPEN_COUNT, COL_AVG_AGE]].head(len(AGE_LABELS)))}

The inventory links each open issue to an injected facility. Closed examples are a separate assumed history.
The closed-history count appears in the historical summary row under the shared count column.

### Checklist and next steps

The illustrative principles 1 to 11 checklist averages {bcbs[COL_SCORE_0_TO_3].mean():.2f}/3 on a project-defined evidence scale.
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
"""
    with open(MEMO_PATH, "w", encoding="utf-8") as handle:
        handle.write(memo)
    print(f"SYNTHETIC two-section memo written: {MEMO_PATH}")
    return memo

if __name__ == "__main__":
    build_executive_memo()
