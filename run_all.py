import os
import sys
import time

# CONFIG
REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from python.config import *

from python.loan_tape_generator import save_generated_datasets
from python.fr_y14q_builder import build_fr_y14q_schedule
from python.cecl_engine import compute_cecl_portfolio_reserves
from python.data_governance_catalog import run_data_governance_profiling
from python.bcbs_239_assessment import evaluate_bcbs_239_principles
from python.reconciliation_engine import run_reconciliation
from python.memo_generator import build_executive_memo
from python.visualizer import generate_visual_charts

from tests.test_review_regressions import test_review_regressions
from tests.test_schedule_tie_out import test_schedule_ties_to_loan_tape
from tests.test_dq_defect_detection import test_all_injected_dq_defects_detected
from tests.test_cecl_roll_forward import test_cecl_reserve_consistency
from tests.test_reconciliation_rules import test_reconciliation_rules_and_tolerances

def run_all_pipeline():

    start_time = time.time()
    print("================================================================================")
    print("STARTING REGULATORY REPORTING AND DATA GOVERNANCE PACK PIPELINE")
    print("================================================================================")

    print("\n[Step 1/8] Generating Synthetic Wholesale Loan Tape (5,000 Loans)...")
    save_generated_datasets()

    print("\n[Step 2/8] Building FR Y-14Q Schedule H.1 and Data Dictionary...")
    build_fr_y14q_schedule()

    print("\n[Step 3/8] Computing CECL Quantitative Loss Reserves and Qualitative Overlays...")
    compute_cecl_portfolio_reserves()

    print("\n[Step 4/8] Building Metadata Catalog and Evaluating 18 DQ Checkpoints...")
    run_data_governance_profiling()

    print("\n[Step 5/8] Performing BCBS 239 Principles 1 to 11 Project Evidence Checklist...")
    evaluate_bcbs_239_principles()

    print("\n[Step 6/8] Executing FR 2052a to General Ledger Reconciliation...")
    run_reconciliation()

    print("\n[Step 7/8] Generating Two-Page Executive Memorandum...")
    build_executive_memo()

    print("\n[Step 8/8] Rendering Visual Analytics Charts...")
    generate_visual_charts()

    print("\n================================================================================")
    print("RUNNING VERIFICATION TEST SUITES")
    print("================================================================================")
    
    print("\n[Test 1/5] Running FR Y-14Q Schedule to Loan Tape Tie-Out Test...")
    test_schedule_ties_to_loan_tape()
    
    print("\n[Test 2/5] Running Data Quality Injected Defect Detection Test...")
    test_all_injected_dq_defects_detected()
    
    print("\n[Test 3/5] Running CECL Reserve Roll-Forward Accounting Consistency Test...")
    test_cecl_reserve_consistency()
    
    print("\n[Test 4/5] Running Reconciliation Tolerance and Break Aging Test...")
    test_reconciliation_rules_and_tolerances()
    
    print("\n[Test 5/5] Running Reviewer Regression and Independent Arithmetic Checks...")
    test_review_regressions()

    elapsed = time.time() - start_time
    print("\n================================================================================")
    print(f"PIPELINE RUN COMPLETE: All steps and test suites passed in {elapsed:.2f} seconds.")
    print("================================================================================")

if __name__ == "__main__":
    run_all_pipeline()
