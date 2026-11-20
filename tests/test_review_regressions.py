import csv
import os
import sys
from datetime import date
from decimal import Decimal
from math import fsum
import numpy as np
import pandas as pd

# CONFIG
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT) if REPO_ROOT not in sys.path else None
from python.config import *
from python.data_governance_catalog import dq_failure_masks, evaluate_dq_rules
from python.reconciliation_engine import classify_reconciliation
REVIEW_NUMBERS_PATH = os.path.join(OUTPUTS_DIR, "review_independent_numbers.csv")
COL_RECOMPUTED = "independently_recomputed"
COL_REPORTED = "reported"
COL_DIFFERENCE = "difference"
WEIGHT_TOLERANCE = 1e-12
RECON_BOUNDARY_CASES = [(100.0, 0.0, "Immaterial Cleared"), (101.0, 0.0, "Active Break"), (0.0, 0.0, "Immaterial Cleared"), (10000100.0, 10000000.0, "Immaterial Cleared"), (20010000.0, 20000000.0, "In Tolerance"), (20010000.01, 20000000.0, "Active Break"), (1000500.01, 1000000.0, "Active Break"), (1000500.0, 1000000.0, "In Tolerance"), (-999000.0, -1000000.0, "Active Break")]
EDGE_BAD_DATE = "not-a-date"
EDGE_COLLATERAL_ID = "UNMAPPED"
EDGE_FACILITY_ID = "UNKNOWN"
EDGE_SHORT_LEI = "123"
EDGE_NEGATIVE = -1.0
EDGE_ROW_COUNT = 10

def test_review_regressions():
    tape = pd.read_csv(LOAN_TAPE_CLEAN_PATH, dtype={COL_BORROWER_LEI: str})
    defects = pd.read_csv(LOAN_TAPE_DEFECTS_PATH, dtype={COL_BORROWER_LEI: str})
    expected = set(defects.loc[defects[COL_IS_DEFECTIVE], COL_FACILITY_ID])
    masks = dq_failure_masks(defects)
    actual = set(defects.loc[pd.DataFrame(masks).any(axis=1), COL_FACILITY_ID])
    assert actual == expected, "Missed defective facility or flagged clean facility"
    assert not pd.DataFrame(dq_failure_masks(tape)).any().any()
    assert evaluate_dq_rules(defects).set_index(COL_DQ_RULE_ID)[COL_FAIL_COUNT].to_dict() == DQ_EXPECTED_FAILURES
    edge = tape.head(EDGE_ROW_COUNT).copy()
    edge.loc[0, COL_BORROWER_ID] = np.nan
    edge.loc[1, COL_BORROWER_LEI] = EDGE_SHORT_LEI
    edge.loc[2, COL_FACILITY_ID] = edge.loc[3, COL_FACILITY_ID]
    edge.loc[4, COL_DRAWN_BALANCE] = EDGE_NEGATIVE
    edge.loc[5, COL_COLLATERAL_ID] = EDGE_COLLATERAL_ID
    edge.loc[6, COL_MATURITY_DATE] = EDGE_BAD_DATE
    edge.loc[7, COL_COMMITTED_EXPOSURE] = np.inf
    edge.loc[8, COL_FACILITY_ID] = EDGE_FACILITY_ID
    edge.loc[9, COL_BORROWER_LEI] = np.nan
    bad = dq_failure_masks(edge)
    for rule, indices in [("DQ_COMP_01", [0]), ("DQ_COMP_02", [1, 9]), ("DQ_COMP_03", [2, 3]), ("DQ_RSN_01", [4]), ("DQ_REF_01", [5, 8]), ("DQ_RSN_03", [6]), ("DQ_VAL_02", [7])]:
        assert bad[rule].loc[indices].all(), rule
    schedule = pd.read_csv(FR_Y14Q_SCHEDULE_OUTPUT_PATH, dtype={COL_BORROWER_LEI: str})
    dictionary = pd.read_csv(FR_Y14Q_DICT_PATH)
    catalog = pd.read_csv(METADATA_CATALOG_PATH)
    assert set(schedule.columns) == set(dictionary[COL_FIELD_NAME]) == set(catalog[COL_FIELD_NAME])
    assert not catalog.isna().any().any()
    assert not catalog[COL_DQ_RULE_ID].eq("Not implemented").any()
    for field in schedule.columns:
        null_case = tape.head(1).astype(object).copy()
        null_case.loc[0, field] = None
        assert pd.DataFrame(dq_failure_masks(null_case)).any(axis=1).item(), field
    pd.testing.assert_frame_equal(tape[schedule.columns].set_index(COL_FACILITY_ID).sort_index(), schedule.set_index(COL_FACILITY_ID).sort_index(), check_dtype=False)
    issues = pd.read_csv(DQ_ISSUES_PATH)
    assert set(issues[COL_FACILITY_ID]) == expected
    closed = pd.read_csv(DQ_CLOSED_PATH)
    aging = pd.read_csv(DQ_AGING_PATH)
    assert aging.loc[aging[COL_AGE_BUCKET].eq("HISTORICAL CLOSED (MTTC)"), COL_OPEN_COUNT].item() == len(closed)
    assert abs(aging.loc[aging[COL_AGE_BUCKET].eq("HISTORICAL CLOSED (MTTC)"), COL_AVG_AGE].item() - closed[COL_CLOSE_DAYS].mean()) < MONEY_TOLERANCE
    for bucket, group in issues.groupby(COL_AGE_BUCKET):
        assert aging.loc[aging[COL_AGE_BUCKET].eq(bucket), COL_OPEN_COUNT].item() == len(group)
    for schedule_amount, gl_amount, expected_flag in RECON_BOUNDARY_CASES:
        case = pd.DataFrame([{COL_SCHEDULE_AMOUNT: schedule_amount, COL_GL_AMOUNT: gl_amount, COL_BREAK_AGE_DAYS: RECON_AGE_LIMITS[2]}])
        result = classify_reconciliation(case)
        assert result[COL_BREAK_FLAG].item() == expected_flag, (schedule_amount, gl_amount)
    facilities = pd.read_csv(CECL_FACILITY_PATH)
    assert facilities[COL_LIFETIME_PD].between(0, 1).all()
    assert facilities[COL_LGD].between(0, 1).all()
    assert facilities[COL_EAD].ge(facilities[COL_DRAWN_BALANCE] - MONEY_TOLERANCE).all()
    assert facilities[COL_EAD].le(facilities[COL_COMMITTED_EXPOSURE] + MONEY_TOLERANCE).all()
    cohorts = pd.read_csv(CECL_COHORT_PATH)
    for row in cohorts.to_dict("records"):
        group = facilities.loc[facilities[COL_RISK_RATING].eq(row[COL_RISK_RATING])]
        low, high = TENOR_BREAKS
        bucket = row[COL_TENOR_BUCKET]
        selected = group.loc[group[COL_TENOR_YEARS].le(low)] if bucket.startswith("Short") else group.loc[group[COL_TENOR_YEARS].gt(high)] if bucket.startswith("Long") else group.loc[group[COL_TENOR_YEARS].gt(low) & group[COL_TENOR_YEARS].le(high)]
        assert len(selected) == row[COL_FACILITY_COUNT]
        assert abs((selected[COL_LIFETIME_PD] * selected[COL_EAD]).sum() / selected[COL_EAD].sum() - row[COL_WEIGHTED_PD]) < WEIGHT_TOLERANCE
    # Scalar arithmetic avoids sharing vectorized calculation logic.
    with open(LOAN_TAPE_CLEAN_PATH, encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    commitment = sum(Decimal(row[COL_COMMITTED_EXPOSURE]) for row in records)
    reserve_terms = []
    for row in records:
        tenor = max((date.fromisoformat(row[COL_MATURITY_DATE]) - date.fromisoformat(REPORTING_DATE)).days / DAYS_PER_YEAR, 0)
        rating = int(row[COL_RISK_RATING])
        pd_lifetime = 1 - pow(1 - RATING_ANNUAL_PD[rating], tenor)
        ead = round(float(row[COL_DRAWN_BALANCE]) + float(row[COL_UNDRAWN_COMMITMENT]) * CREDIT_CONVERSION_FACTOR[row[COL_FACILITY_TYPE]], 2)
        base = round(ead * pd_lifetime * COLLATERAL_LGD[row[COL_COLLATERAL_TYPE]], 2)
        overlay_rate = OVERLAY_BASE
        if row[COL_COLLATERAL_TYPE] == "Commercial Real Estate":
            overlay_rate += OVERLAY_CRE
        if rating >= CRITICIZED_RATING:
            overlay_rate += OVERLAY_CRITICIZED
        reserve_terms.append(base + round(base * overlay_rate, 2))
    recomputed_acl = round(fsum(reserve_terms), 2)
    with open(RECON_BREAKS_PATH, encoding="utf-8", newline="") as handle:
        breaks = list(csv.DictReader(handle))
    gross = sum(abs(Decimal(row[COL_SCHEDULE_AMOUNT]) - Decimal(row[COL_GL_AMOUNT])) for row in breaks if row[COL_BREAK_FLAG] == "Active Break")
    summary = pd.read_csv(RECON_SUMMARY_PATH).set_index(COL_SUMMARY_METRIC)[COL_METRIC_VALUE]
    reported = [round(schedule[COL_COMMITTED_EXPOSURE].sum(), 2), round(facilities[COL_TOTAL_RESERVE].sum(), 2), summary.loc["Gross Absolute Break Variance ($)"]]
    independent = [float(commitment), recomputed_acl, float(gross)]
    rows = []
    for label, recomputed, value in zip(["Commitments ($)", "Ending ACL ($)", "Gross active breaks ($)"], independent, reported):
        difference = round(recomputed - value, 2)
        assert abs(difference) < MONEY_TOLERANCE
        rows.append({COL_METRIC_NAME: label, COL_RECOMPUTED: recomputed, COL_REPORTED: value, COL_DIFFERENCE: difference})
    pd.DataFrame(rows).to_csv(REVIEW_NUMBERS_PATH, index=False)
    print("PASS: record detection, edge cases, metadata, issue linkage, CECL cohorts and three independent recomputations")
    print(pd.DataFrame(rows).to_string(index=False))

if __name__ == "__main__":
    test_review_regressions()
