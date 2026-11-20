import os
import sys
import pandas as pd
import numpy as np

# CONFIG
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from python.config import *

def test_schedule_ties_to_loan_tape():

    if not os.path.exists(LOAN_TAPE_CLEAN_PATH):
        from python.loan_tape_generator import save_generated_datasets
        save_generated_datasets()
    if not os.path.exists(FR_Y14Q_SCHEDULE_OUTPUT_PATH) or not os.path.exists(FR_Y14Q_DICT_PATH):
        from python.fr_y14q_builder import build_fr_y14q_schedule
        build_fr_y14q_schedule()
        
    assert os.path.exists(LOAN_TAPE_CLEAN_PATH), f"Missing clean loan tape at {LOAN_TAPE_CLEAN_PATH}"
    assert os.path.exists(FR_Y14Q_SCHEDULE_OUTPUT_PATH), f"Missing schedule at {FR_Y14Q_SCHEDULE_OUTPUT_PATH}"
    assert os.path.exists(FR_Y14Q_DICT_PATH), f"Missing field dictionary at {FR_Y14Q_DICT_PATH}"
    
    tape_df = pd.read_csv(LOAN_TAPE_CLEAN_PATH)
    schedule_df = pd.read_csv(FR_Y14Q_SCHEDULE_OUTPUT_PATH)
    dict_df = pd.read_csv(FR_Y14Q_DICT_PATH)

    print(f"Testing record count: Tape={len(tape_df):,}, Schedule={len(schedule_df):,}")
    assert len(tape_df) == TOTAL_LOAN_COUNT, f"Expected {TOTAL_LOAN_COUNT} loans in tape"
    assert len(schedule_df) == TOTAL_LOAN_COUNT, f"Expected {TOTAL_LOAN_COUNT} loans in schedule"
    assert len(tape_df) == len(schedule_df), "Mismatch in total record count between tape and schedule"

    tape_committed = tape_df[COL_COMMITTED_EXPOSURE].sum()
    sched_committed = schedule_df[COL_COMMITTED_EXPOSURE].sum()
    committed_diff = abs(tape_committed - sched_committed)
    print(f"Testing committed exposure tie-out: Diff=${committed_diff:.2f}")
    assert committed_diff < MONEY_TOLERANCE, f"Committed exposure mismatch: Diff=${committed_diff:.2f}"

    tape_drawn = tape_df[COL_DRAWN_BALANCE].sum()
    sched_utilized = schedule_df[COL_UTILIZED_EXPOSURE].sum()
    drawn_diff = abs(tape_drawn - sched_utilized)
    print(f"Testing drawn balance tie-out: Diff=${drawn_diff:.2f}")
    assert drawn_diff < MONEY_TOLERANCE, f"Drawn balance mismatch: Diff=${drawn_diff:.2f}"

    tape_collateral = tape_df[COL_COLLATERAL_VALUE].sum()
    sched_collateral = schedule_df[COL_COLLATERAL_VALUE].sum()
    collateral_diff = abs(tape_collateral - sched_collateral)
    print(f"Testing collateral valuation tie-out: Diff=${collateral_diff:.2f}")
    assert collateral_diff < MONEY_TOLERANCE, f"Collateral value mismatch: Diff=${collateral_diff:.2f}"

    tape_unique_facs = tape_df[COL_FACILITY_ID].nunique()
    sched_unique_facs = schedule_df[COL_FACILITY_ID].nunique()
    print(f"Testing unique facility IDs: Tape={tape_unique_facs:,}, Schedule={sched_unique_facs:,}")
    assert tape_unique_facs == TOTAL_LOAN_COUNT, "Non-unique facility IDs present in loan tape"
    assert sched_unique_facs == TOTAL_LOAN_COUNT, "Non-unique facility IDs present in schedule"

    print(f"Testing field dictionary entries count: {len(dict_df)}")
    assert len(dict_df) >= 15, "Field dictionary must cover at least 15 schedule items"
    assert COL_DICT_CDE_FLAG in dict_df.columns, "CDE flag column missing from dictionary"
    
    print("PASS: FR Y-14Q Schedule H.1 perfectly ties to the loan tape totals.")

if __name__ == "__main__":
    test_schedule_ties_to_loan_tape()
