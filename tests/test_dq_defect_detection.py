import os
import sys
import pandas as pd
import numpy as np

# CONFIG
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from python.config import *
from python.data_governance_catalog import evaluate_dq_rules

def test_all_injected_dq_defects_detected():

    if not os.path.exists(LOAN_TAPE_DEFECTS_PATH):
        from python.loan_tape_generator import save_generated_datasets
        save_generated_datasets()
        
    assert os.path.exists(LOAN_TAPE_DEFECTS_PATH), f"Missing defect tape at {LOAN_TAPE_DEFECTS_PATH}"
    defects_df = pd.read_csv(LOAN_TAPE_DEFECTS_PATH, dtype={COL_BORROWER_LEI: str})

    injected_count = defects_df[COL_IS_DEFECTIVE].sum()
    print(f"Total synthetic defects injected in test tape: {injected_count}")
    assert injected_count == 150, f"Expected 150 injected defects, found {injected_count}"

    results_df = evaluate_dq_rules(defects_df)
    results_map = results_df.set_index(COL_DQ_RULE_ID)[COL_FAIL_COUNT].to_dict()

    lei_fails = results_map.get("DQ_COMP_02", 0)
    print(f"Testing Rule DQ_COMP_02 (LEI Completeness): Failures Detected={lei_fails} (Expected 30)")
    assert lei_fails == 30, f"Expected 30 LEI failures, got {lei_fails}"

    rating_fails = results_map.get("DQ_VAL_03", 0)
    print(f"Testing Rule DQ_VAL_03 (Risk Rating Validity): Failures Detected={rating_fails} (Expected 25)")
    assert rating_fails == 25, f"Expected 25 rating failures, got {rating_fails}"

    col_fails = results_map.get("DQ_RSN_02", 0)
    print(f"Testing Rule DQ_RSN_02 (Collateral Non-Negative): Failures Detected={col_fails} (Expected 25)")
    assert col_fails == 25, f"Expected 25 collateral failures, got {col_fails}"

    drawn_fails = results_map.get("DQ_RSN_01", 0)
    print(f"Testing Rule DQ_RSN_01 (Drawn <= Committed): Failures Detected={drawn_fails} (Expected 25)")
    assert drawn_fails == 25, f"Expected 25 overdrawn balance failures, got {drawn_fails}"

    date_fails = results_map.get("DQ_RSN_03", 0)
    print(f"Testing Rule DQ_RSN_03 (Maturity >= Origination): Failures Detected={date_fails} (Expected 25)")
    assert date_fails == 25, f"Expected 25 date logic failures, got {date_fails}"

    borr_fails = results_map.get("DQ_COMP_01", 0)
    print(f"Testing Rule DQ_COMP_01 (Borrower ID Completeness): Failures Detected={borr_fails} (Expected 20)")
    assert borr_fails == 20, f"Expected 20 borrower completeness failures, got {borr_fails}"

    total_detected = (
        lei_fails + rating_fails + col_fails + drawn_fails + date_fails + borr_fails
    )
    print(f"Total defects detected across all rules: {total_detected} / {injected_count}")
    assert total_detected == injected_count, (
        f"Defect detection discrepancy: detected {total_detected} vs injected {injected_count}"
    )
    
    print("PASS: 100% of injected data quality defects were successfully detected.")

if __name__ == "__main__":
    test_all_injected_dq_defects_detected()
