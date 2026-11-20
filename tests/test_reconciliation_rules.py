import os
import sys
import pandas as pd
import numpy as np

# CONFIG
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from python.config import *

def test_reconciliation_rules_and_tolerances():

    if not os.path.exists(RECON_BREAKS_PATH) or not os.path.exists(RECON_SUMMARY_PATH):
        from python.reconciliation_engine import run_reconciliation
        run_reconciliation()
        
    assert os.path.exists(RECON_BREAKS_PATH), f"Missing reconciliation breaks at {RECON_BREAKS_PATH}"
    assert os.path.exists(RECON_SUMMARY_PATH), f"Missing summary at {RECON_SUMMARY_PATH}"
    
    recon_df = pd.read_csv(RECON_BREAKS_PATH)

    computed_variance = (recon_df[COL_SCHEDULE_AMOUNT] - recon_df[COL_GL_AMOUNT]).round(2)
    var_diff = (recon_df[COL_VARIANCE_AMOUNT] - computed_variance).abs().max()
    print(f"Testing variance calculation accuracy: Max diff={var_diff:.4f}")
    assert var_diff < MONEY_TOLERANCE, "Variance column does not equal Schedule Amount minus GL Amount"

    for _, row in recon_df.iterrows():
        var_abs = abs(row[COL_VARIANCE_AMOUNT])
        flag = row[COL_BREAK_FLAG]
        
        if var_abs <= RECON_IMMATERIAL_THRESHOLD:
            assert flag == "Immaterial Cleared", (
                f"Variance {var_abs} <= {RECON_IMMATERIAL_THRESHOLD} should be Immaterial Cleared, got {flag}"
            )
        elif var_abs > RECON_TOLERANCE_DOLLARS:
            assert flag == "Active Break", (
                f"Variance {var_abs} > {RECON_TOLERANCE_DOLLARS} should be Active Break, got {flag}"
            )

    active_breaks = recon_df[recon_df[COL_BREAK_FLAG] == "Active Break"]
    print(f"Active breaks identified: {len(active_breaks)}")
    assert len(active_breaks) == 4, f"Expected 4 active breaks, found {len(active_breaks)}"
    
    expected_root_causes = {
        "Cutoff Timing Mismatch",
        "Manual Journal Entry",
        "Unmapped Facility Product Code",
        "Synthetic Valuation Adjustment"
    }
    actual_root_causes = set(active_breaks[COL_ROOT_CAUSE_TAG].tolist())
    print(f"Actual root causes: {actual_root_causes}")
    assert expected_root_causes == actual_root_causes, (
        f"Mismatch in root cause tags: expected {expected_root_causes}, got {actual_root_causes}"
    )

    escalated_breaks = active_breaks[active_breaks[COL_BREAK_AGE_DAYS] > 30]
    print(f"Breaks aged > 30 days (escalated): {len(escalated_breaks)}")
    assert len(escalated_breaks) >= 1, "Expected at least 1 escalated break aged > 30 days"
    for _, row in escalated_breaks.iterrows():
        assert row[COL_BREAK_AGE_BUCKET] == "> 30 Days (Escalated)", (
            f"Expected bucket '> 30 Days (Escalated)', got {row[COL_BREAK_AGE_BUCKET]}"
        )
        
    print("PASS: Reconciliation breaks, tolerance rules, and aging logic verified.")

if __name__ == "__main__":
    test_reconciliation_rules_and_tolerances()
