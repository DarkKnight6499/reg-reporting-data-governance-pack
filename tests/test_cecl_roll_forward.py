import os
import sys
import pandas as pd
import numpy as np

# CONFIG
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from python.config import *

def test_cecl_reserve_consistency():

    if not os.path.exists(CECL_ROLL_FORWARD_PATH) or not os.path.exists(CECL_COHORT_PATH):
        from python.cecl_engine import compute_cecl_portfolio_reserves
        compute_cecl_portfolio_reserves()
        
    assert os.path.exists(CECL_ROLL_FORWARD_PATH), f"Missing roll-forward at {CECL_ROLL_FORWARD_PATH}"
    assert os.path.exists(CECL_COHORT_PATH), f"Missing cohort analysis at {CECL_COHORT_PATH}"
    assert os.path.exists(CECL_SUMMARY_PATH), f"Missing summary at {CECL_SUMMARY_PATH}"
    
    rf_df = pd.read_csv(CECL_ROLL_FORWARD_PATH)
    cohort_df = pd.read_csv(CECL_COHORT_PATH)
    summary_df = pd.read_csv(CECL_SUMMARY_PATH)

    def get_amt(label):
        match = rf_df[rf_df[COL_COMPONENT].eq("Ending Allowance")] if label == "Ending" else rf_df[rf_df[COL_COMPONENT].str.contains(label, case=False)]
        assert not match.empty, f"Could not find roll-forward row for {label}"
        return match[COL_AMOUNT].values[0]
        
    beg_acl = get_amt("Beginning")
    provision = get_amt("Provision Expense")
    base_loss = get_amt("Base Model")
    overlay = get_amt("Qualitative Economic")
    gross_co = get_amt("Gross Charge-offs")
    recoveries = get_amt("Recoveries")
    net_co = get_amt("Net Charge-offs")
    ending_acl = get_amt("Ending")
    
    print(f"Beginning ACL:   ${beg_acl:,.2f}")
    print(f"Provision:       ${provision:,.2f}")
    print(f"  Base Model:    ${base_loss:,.2f}")
    print(f"  Overlay:       ${overlay:,.2f}")
    print(f"Net Charge-offs: ${net_co:,.2f}")
    print(f"Ending ACL:      ${ending_acl:,.2f}")

    calculated_net_co = gross_co + recoveries
    assert abs(net_co - calculated_net_co) < MONEY_TOLERANCE, (
        f"Net charge-offs mismatch: {net_co} vs {calculated_net_co}"
    )

    assert abs(ending_acl - base_loss - overlay) < MONEY_TOLERANCE

    expected_ending = beg_acl + provision + net_co
    diff = abs(ending_acl - expected_ending)
    print(f"Roll-forward tie-out discrepancy: ${diff:.4f}")
    assert diff < MONEY_TOLERANCE, f"CECL roll-forward arithmetic failed: Diff=${diff:.4f}"

    assert len(cohort_df) > 0, "Cohort summary is empty"
    total_cohort_acl = cohort_df[COL_TOTAL_ACL].sum()
    cohort_diff = abs(ending_acl - total_cohort_acl)
    print(f"Cohort ACL tie-out to total reserve: Diff=${cohort_diff:.2f}")
    assert cohort_diff < MONEY_TOLERANCE, f"Cohort reserve total {total_cohort_acl} does not match ending ACL {ending_acl}"

    pass_cov = cohort_df[cohort_df[COL_RATING_TIER].str.contains("Pass")][COL_ACL_COVERAGE].mean()
    classified_cov = cohort_df[cohort_df[COL_RATING_TIER].str.contains("Classified")][COL_ACL_COVERAGE].mean()
    print(f"Pass Tier Coverage: {pass_cov:.2f}%, Classified Tier Coverage: {classified_cov:.2f}%")
    assert classified_cov > pass_cov, "Classified loans must have higher CECL coverage than pass loans"
    
    print("PASS: CECL reserve calculations and roll-forward balances tie out perfectly.")

if __name__ == "__main__":
    test_cecl_reserve_consistency()
