import os
import sys
import pandas as pd
import numpy as np

# CONFIG
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT) if REPO_ROOT not in sys.path else None
from python.config import *
from python.fr_y14q_builder import build_field_dictionary

DQ_RULE_DEFINITIONS = {
        "DQ_COMP_01": (COL_BORROWER_ID, "Completeness", "Non-null, non-blank borrower ID"),
        "DQ_COMP_02": (COL_BORROWER_LEI, "Completeness", "Populated 20-character alphanumeric synthetic LEI; no checksum validation"),
        "DQ_COMP_03": (COL_FACILITY_ID, "Completeness", "Populated unique facility ID"),
        "DQ_VAL_01": (COL_FACILITY_TYPE, "Validity", "Product belongs to configured taxonomy"),
        "DQ_VAL_02": (COL_COMMITTED_EXPOSURE, "Validity", "Finite positive commitment"),
        "DQ_RSN_01": (COL_DRAWN_BALANCE, "Reasonableness", "Finite non-negative drawn balance within commitment tolerance; utilized exposure equals drawn"),
        "DQ_VAL_03": (COL_RISK_RATING, "Validity", "Integer rating in configured scale"),
        "DQ_RSN_02": (COL_COLLATERAL_VALUE, "Reasonableness", "Finite non-negative collateral value"),
        "DQ_RSN_03": (COL_MATURITY_DATE, "Reasonableness", "Valid maturity on or after valid origination"),
        "DQ_REF_01": (COL_COLLATERAL_ID, "Referential", "Facility and collateral pair exists in clean synthetic reference"),
    }

DQ_RULE_DEFINITIONS.update({
    "DQ_VAL_04": (COL_BORROWER_NAME, "Validity", "Borrower name is populated"),
    "DQ_VAL_05": (COL_INDUSTRY_NAICS, "Validity", "Industry code belongs to configured synthetic sectors"),
    "DQ_RSN_04": (COL_UTILIZATION_RATE, "Reasonableness", "Finite utilization in zero to one range agrees with drawn divided by commitment"),
    "DQ_VAL_06": (COL_RATING_GRADE_DESC, "Validity", "Rating description matches configured grade"),
    "DQ_VAL_07": (COL_COLLATERAL_TYPE, "Validity", "Collateral type belongs to configured taxonomy"),
    "DQ_RSN_05": (COL_ORIGINATION_DATE, "Reasonableness", "Valid origination on or before reporting date"),
    "DQ_VAL_08": (COL_INTEREST_RATE, "Validity", "Finite interest rate within configured limits"),
    "DQ_VAL_09": (COL_CURRENCY, "Validity", "Currency matches synthetic base currency"),
})

def dq_failure_masks(df):
    clean = pd.read_csv(LOAN_TAPE_CLEAN_PATH, dtype={COL_BORROWER_LEI: str})
    present = lambda column: df[column].notna() & df[column].astype(str).str.strip().ne("")
    number = lambda column: pd.to_numeric(df[column], errors="coerce")
    committed = number(COL_COMMITTED_EXPOSURE)
    drawn = number(COL_DRAWN_BALANCE)
    collateral = number(COL_COLLATERAL_VALUE)
    links = clean.set_index(COL_FACILITY_ID)[COL_COLLATERAL_ID]
    masks = {
        "DQ_COMP_01": ~present(COL_BORROWER_ID),
        "DQ_COMP_02": ~(present(COL_BORROWER_LEI) & df[COL_BORROWER_LEI].astype(str).str.fullmatch(LEI_SHAPE_PATTERN, na=False)),
        "DQ_COMP_03": ~present(COL_FACILITY_ID) | df[COL_FACILITY_ID].duplicated(keep=False),
        "DQ_VAL_01": ~df[COL_FACILITY_TYPE].isin(FACILITY_TYPES),
        "DQ_VAL_02": ~(np.isfinite(committed) & committed.gt(0)),
        "DQ_RSN_01": ~(np.isfinite(drawn) & drawn.ge(0) & drawn.le(committed + MONEY_TOLERANCE) & np.isfinite(number(COL_UTILIZED_EXPOSURE)) & (number(COL_UTILIZED_EXPOSURE) - drawn).abs().le(MONEY_TOLERANCE)),
        "DQ_VAL_03": ~number(COL_RISK_RATING).isin(RATING_DESCRIPTIONS),
        "DQ_RSN_02": ~(np.isfinite(collateral) & collateral.ge(0)),
        "DQ_RSN_03": ~(pd.to_datetime(df[COL_MATURITY_DATE], errors="coerce") >= pd.to_datetime(df[COL_ORIGINATION_DATE], errors="coerce")),
        "DQ_VAL_04": ~present(COL_BORROWER_NAME),
        "DQ_VAL_05": ~df[COL_INDUSTRY_NAICS].astype(str).isin([code for code, _ in SECTORS]),
        "DQ_RSN_04": ~(np.isfinite(number(COL_UTILIZATION_RATE)) & number(COL_UTILIZATION_RATE).between(0, 1) & (number(COL_UTILIZATION_RATE) - drawn / committed).abs().le(UTILIZATION_TOLERANCE)),
        "DQ_VAL_06": ~df[COL_RATING_GRADE_DESC].eq(number(COL_RISK_RATING).map(RATING_DESCRIPTIONS)),
        "DQ_VAL_07": ~df[COL_COLLATERAL_TYPE].isin(COLLATERAL_TYPES),
        "DQ_RSN_05": ~pd.to_datetime(df[COL_ORIGINATION_DATE], errors="coerce").le(pd.Timestamp(REPORTING_DATE)),
        "DQ_VAL_08": ~(np.isfinite(number(COL_INTEREST_RATE)) & number(COL_INTEREST_RATE).between(*INTEREST_RATE_LIMITS)),
        "DQ_VAL_09": ~df[COL_CURRENCY].eq(BASE_CURRENCY),
        "DQ_REF_01": ~(present(COL_COLLATERAL_ID) & df[COL_COLLATERAL_ID].eq(df[COL_FACILITY_ID].map(links))),
    }
    return {rule: mask.fillna(True).astype(bool) for rule, mask in masks.items()}


def rule_definitions():
    return DQ_RULE_DEFINITIONS

def evaluate_dq_rules(df):
    if df.empty:
        raise ValueError("Cannot profile empty tape")
    masks = dq_failure_masks(df)
    rows = []
    for rule, (field, dimension, description) in rule_definitions().items():
        failed = int(masks[rule].sum())
        rows.append({COL_DQ_RULE_ID: rule, COL_FIELD_NAME: field, COL_DQ_DIMENSION: dimension,
                     COL_DQ_RULE_DESC: description, COL_TOTAL_RECORDS: len(df), COL_PASS_COUNT: len(df) - failed,
                     COL_FAIL_COUNT: failed, COL_PASS_RATE_PCT: round((len(df) - failed) / len(df) * 100, 2)})
    return pd.DataFrame(rows)

def build_metadata_catalog():
    dictionary = build_field_dictionary()
    entries = []
    for row in dictionary.to_dict("records"):
        field = row[COL_DICT_FIELD_NAME]
        rules = [(rule, dimension, description) for rule, (target, dimension, description) in rule_definitions().items() if target == field or (field == COL_UTILIZED_EXPOSURE and target == COL_DRAWN_BALANCE)]
        entries.append({COL_FIELD_NAME: field, COL_FIELD_DESCRIPTION: row[COL_DICT_DEFINITION],
                        COL_DATA_STEWARD: "Synthetic reporting steward", COL_CDE_FLAG: row[COL_DICT_CDE_FLAG],
                        COL_SOURCE_SYSTEM: "Synthetic Python generator",
                        COL_LINEAGE_HOPS: "loan_tape_generator -> synthetic_wholesale_loan_tape.csv -> fr_y14q_builder -> fr_y14q_schedule_h1.csv",
                        COL_DQ_RULE_ID: "; ".join(rule for rule, _, _ in rules) or "Not implemented",
                        COL_DQ_DIMENSION: "; ".join(dimension for _, dimension, _ in rules) or "Not tested",
                        COL_DQ_RULE_DESC: "; ".join(description for _, _, description in rules) or "No field-specific automated DQ rule; coverage gap"})
    return pd.DataFrame(entries)

def generate_issue_aging_kpis(defects_df):
    defective = defects_df.loc[defects_df[COL_IS_DEFECTIVE]]
    rng = np.random.default_rng(ISSUE_SEED)
    issues = defective[[COL_FACILITY_ID, COL_DEFECT_TYPE]].copy()
    issues[COL_ISSUE_ID] = [f"ISSUE_{i:04d}" for i in range(1, len(issues) + 1)]
    issues[COL_AGE_DAYS] = rng.integers(*ISSUE_AGE_RANGE, size=len(issues))
    issues[COL_AGE_BUCKET] = pd.cut(issues[COL_AGE_DAYS], [-np.inf, *AGE_LIMITS, np.inf], labels=AGE_LABELS)
    issues[COL_ISSUE_STATUS] = "Synthetic open issue"
    issues[COL_REMEDIATION_OWNER] = "Synthetic data steward"
    issues.to_csv(DQ_ISSUES_PATH, index=False)
    closed = pd.DataFrame({COL_ISSUE_ID: [f"CLOSED_{i:04d}" for i in range(1, len(CLOSED_DURATIONS) + 1)], COL_CLOSE_DAYS: CLOSED_DURATIONS})
    closed.to_csv(DQ_CLOSED_PATH, index=False)
    rows = []
    for bucket, group in issues.groupby(COL_AGE_BUCKET, observed=False):
        rows.append({COL_AGE_BUCKET: bucket, COL_OPEN_COUNT: len(group), COL_AVG_AGE: group[COL_AGE_DAYS].mean(), COL_MAX_AGE: group[COL_AGE_DAYS].max(), COL_PCT_OPEN: len(group) / len(issues) * 100 if len(issues) else 0})
    rows.extend([{COL_AGE_BUCKET: "ALL OPEN (TOTAL)", COL_OPEN_COUNT: len(issues), COL_AVG_AGE: issues[COL_AGE_DAYS].mean(), COL_MAX_AGE: issues[COL_AGE_DAYS].max(), COL_PCT_OPEN: 100},
                 {COL_AGE_BUCKET: "HISTORICAL CLOSED (MTTC)", COL_OPEN_COUNT: len(closed), COL_AVG_AGE: closed[COL_CLOSE_DAYS].mean(), COL_MAX_AGE: closed[COL_CLOSE_DAYS].max(), COL_PCT_OPEN: 0}])
    return issues, pd.DataFrame(rows).round(2)

def run_data_governance_profiling():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    catalog = build_metadata_catalog()
    catalog.to_csv(METADATA_CATALOG_PATH, index=False)
    clean = pd.read_csv(LOAN_TAPE_CLEAN_PATH, dtype={COL_BORROWER_LEI: str})
    defects = pd.read_csv(LOAN_TAPE_DEFECTS_PATH, dtype={COL_BORROWER_LEI: str})
    clean_results = evaluate_dq_rules(clean)
    clean_results.to_csv(DQ_CLEAN_RESULTS_PATH, index=False)
    results = evaluate_dq_rules(defects)
    results.to_csv(DQ_RESULTS_PATH, index=False)
    details = []
    for rule, mask in dq_failure_masks(defects).items():
        for facility in defects.loc[mask, COL_FACILITY_ID]:
            details.append({COL_FACILITY_ID: facility, COL_DQ_RULE_ID: rule})
    pd.DataFrame(details, columns=[COL_FACILITY_ID, COL_DQ_RULE_ID]).to_csv(DQ_DETAIL_PATH, index=False)
    issues, aging = generate_issue_aging_kpis(defects)
    aging.to_csv(DQ_AGING_PATH, index=False)
    print(f"SYNTHETIC catalog: {len(catalog)} fields; clean failures: {clean_results[COL_FAIL_COUNT].sum()}; detected defective facilities: {len(set(item[COL_FACILITY_ID] for item in details))}")
    print(aging.to_string(index=False))
    return catalog, results, aging

if __name__ == "__main__":
    run_data_governance_profiling()

