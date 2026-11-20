import os
import sys
import pandas as pd
import numpy as np

# CONFIG
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT) if REPO_ROOT not in sys.path else None
from python.config import *
RECON_PRODUCTS = ["Term drawn (synthetic GL 1050)", "Revolver drawn (synthetic GL 1050)", "Revolver undrawn (synthetic GL 2100)", "Letter of credit commitments (synthetic GL 2100)", "Bridge commitments (synthetic GL 2100)", "Fee clearing residual"]

def classify_reconciliation(recon):
    result = recon.copy()
    if not np.isfinite(result[[COL_SCHEDULE_AMOUNT, COL_GL_AMOUNT, COL_BREAK_AGE_DAYS]].to_numpy(dtype=float)).all() or result[COL_BREAK_AGE_DAYS].lt(0).any():
        raise ValueError("Reconciliation amounts and ages must be finite; ages must be non-negative")
    result[COL_VARIANCE_AMOUNT] = (result[COL_SCHEDULE_AMOUNT] - result[COL_GL_AMOUNT]).round(2)
    absolute = result[COL_VARIANCE_AMOUNT].abs()
    denominator = result[COL_GL_AMOUNT].abs()
    # Keep full precision so rounding cannot hide threshold crossings.
    result[COL_VARIANCE_PCT] = absolute.div(denominator.where(denominator.ne(0))).fillna(np.inf).where(absolute.ne(0), 0)
    immaterial = absolute.le(RECON_IMMATERIAL_THRESHOLD)
    active = (absolute.gt(RECON_TOLERANCE_DOLLARS) | result[COL_VARIANCE_PCT].gt(RECON_TOLERANCE_PCT)) & ~immaterial
    result[COL_BREAK_FLAG] = np.select([immaterial, active], ["Immaterial Cleared", "Active Break"], default="In Tolerance")
    age = result[COL_BREAK_AGE_DAYS]
    result[COL_BREAK_AGE_BUCKET] = np.select([age.eq(0), age.lt(RECON_AGE_LIMITS[0]), age.le(RECON_AGE_LIMITS[1]), age.le(RECON_AGE_LIMITS[2])], ["Reconciled (0 Days)", "< 5 Days", "5-15 Days", "16-30 Days"], default="> 30 Days (Escalated)")
    return result

def run_reconciliation():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    tape = pd.read_csv(LOAN_TAPE_CLEAN_PATH)
    amount = lambda product, column: round(tape.loc[tape[COL_FACILITY_TYPE].eq(product), column].sum(), 2)
    balances = [amount("Term Loan", COL_DRAWN_BALANCE), amount("Revolving Credit", COL_DRAWN_BALANCE),
                amount("Revolving Credit", COL_UNDRAWN_COMMITMENT), amount("Letter of Credit", COL_COMMITTED_EXPOSURE),
                amount("Bridge Loan", COL_COMMITTED_EXPOSURE), RECON_FEE_BALANCE]
    rows = []
    for i, (product, balance, shock, age, cause, owner) in enumerate(zip(RECON_PRODUCTS, balances, RECON_SHOCKS, RECON_AGES, RECON_CAUSES, RECON_OWNERS), 1):
        rows.append({COL_RECON_ID: f"REC_{i:03d}", COL_PRODUCT_DESC: product, COL_SCHEDULE_AMOUNT: balance,
                     COL_GL_AMOUNT: round(balance - shock, 2), COL_BREAK_AGE_DAYS: age,
                     COL_ROOT_CAUSE_TAG: cause, COL_REMEDIATION_OWNER: owner,
                     COL_NARRATIVE: "SYNTHETIC scenario label assigned during generation; not inferred from evidence"})
    base = pd.DataFrame(rows)
    base[[COL_RECON_ID, COL_PRODUCT_DESC, COL_SCHEDULE_AMOUNT]].to_csv(RECON_SCHEDULE_PATH, index=False)
    base[[COL_RECON_ID, COL_GL_AMOUNT]].to_csv(RECON_GL_PATH, index=False)
    # Merge persisted inputs to exercise the reporting and ledger key match.
    schedule = pd.read_csv(RECON_SCHEDULE_PATH)
    ledger = pd.read_csv(RECON_GL_PATH)
    joined = schedule.merge(ledger, on=COL_RECON_ID, how="outer", validate="one_to_one", indicator=True)
    if not joined[COL_MERGE_STATUS].eq("both").all():
        raise ValueError("Unmatched synthetic reporting or GL key")
    joined = joined.drop(columns=COL_MERGE_STATUS).merge(base[[COL_RECON_ID, COL_BREAK_AGE_DAYS, COL_ROOT_CAUSE_TAG, COL_REMEDIATION_OWNER, COL_NARRATIVE]], on=COL_RECON_ID, validate="one_to_one")
    recon = classify_reconciliation(joined)
    recon.to_csv(RECON_BREAKS_PATH, index=False)
    active = recon.loc[recon[COL_BREAK_FLAG].eq("Active Break")]
    metrics = [("Total Schedule Exposure ($)", recon[COL_SCHEDULE_AMOUNT].sum()),
               ("Total General Ledger Balance ($)", recon[COL_GL_AMOUNT].sum()),
               ("Total Active Breaks Count", len(active)),
               ("Gross Absolute Break Variance ($)", active[COL_VARIANCE_AMOUNT].abs().sum()),
               ("Net Variance ($)", active[COL_VARIANCE_AMOUNT].sum()),
               ("Breaks Aged > 30 Days (Escalated)", active[COL_BREAK_AGE_DAYS].gt(RECON_AGE_LIMITS[2]).sum())]
    summary = pd.DataFrame([{COL_SUMMARY_METRIC: label, COL_METRIC_VALUE: value} for label, value in metrics])
    summary.to_csv(RECON_SUMMARY_PATH, index=False)
    print("SYNTHETIC reconciliation:\n" + summary.to_string(index=False))
    return recon, summary

if __name__ == "__main__":
    run_reconciliation()
