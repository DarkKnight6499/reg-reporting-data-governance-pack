import os
import sys
import pandas as pd
import numpy as np

# CONFIG
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT) if REPO_ROOT not in sys.path else None
from python.config import *

def compute_cecl_portfolio_reserves():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    tape = pd.read_csv(LOAN_TAPE_CLEAN_PATH, dtype={COL_BORROWER_LEI: str})
    tape[COL_TENOR_YEARS] = ((pd.to_datetime(tape[COL_MATURITY_DATE]) - pd.Timestamp(REPORTING_DATE)).dt.days / DAYS_PER_YEAR).clip(lower=0)
    tape[COL_ANNUAL_PD] = tape[COL_RISK_RATING].map(RATING_ANNUAL_PD)
    tape[COL_LIFETIME_PD] = 1 - (1 - tape[COL_ANNUAL_PD]) ** tape[COL_TENOR_YEARS]
    tape[COL_LGD] = tape[COL_COLLATERAL_TYPE].map(COLLATERAL_LGD)
    ccf = tape[COL_FACILITY_TYPE].map(CREDIT_CONVERSION_FACTOR)
    if tape[[COL_ANNUAL_PD, COL_LGD]].isna().any().any() or ccf.isna().any():
        raise ValueError("Unmapped synthetic credit parameter")
    tape[COL_EAD] = (tape[COL_DRAWN_BALANCE] + tape[COL_UNDRAWN_COMMITMENT] * ccf).map(lambda value: round(float(value), 2))
    tape[COL_BASE_LIFETIME_LOSS] = (tape[COL_EAD] * tape[COL_LIFETIME_PD] * tape[COL_LGD]).map(lambda value: round(float(value), 2))
    overlay = OVERLAY_BASE + OVERLAY_CRE * tape[COL_COLLATERAL_TYPE].eq("Commercial Real Estate") + OVERLAY_CRITICIZED * tape[COL_RISK_RATING].ge(CRITICIZED_RATING)
    tape[COL_QUALITATIVE_OVERLAY] = (tape[COL_BASE_LIFETIME_LOSS] * overlay).map(lambda value: round(float(value), 2))
    tape[COL_TOTAL_RESERVE] = (tape[COL_BASE_LIFETIME_LOSS] + tape[COL_QUALITATIVE_OVERLAY]).map(lambda value: round(float(value), 2))
    tape[COL_RATING_TIER] = np.select([tape[COL_RISK_RATING].lt(CRITICIZED_RATING - 1), tape[COL_RISK_RATING].eq(CRITICIZED_RATING - 1)], ["Pass (Grades 1-4)", "Special Mention (Grade 5)"], default="Classified (Grades 6-8)")
    tape[COL_TENOR_BUCKET] = pd.cut(tape[COL_TENOR_YEARS], [-np.inf, *TENOR_BREAKS, np.inf], labels=["Short (up to 2 years)", "Medium (over 2 to 5 years)", "Long (over 5 years)"])
    tape.to_csv(CECL_FACILITY_PATH, index=False)
    rows = []
    for (rating, tenor), group in tape.groupby([COL_RISK_RATING, COL_TENOR_BUCKET], observed=True):
        ead = group[COL_EAD].sum()
        drawn = group[COL_DRAWN_BALANCE].sum()
        acl = group[COL_TOTAL_RESERVE].sum()
        rows.append({COL_RISK_RATING: rating, COL_RATING_TIER: group[COL_RATING_TIER].iat[0], COL_TENOR_BUCKET: tenor,
                     COL_FACILITY_COUNT: len(group), COL_TOTAL_COMMITTED: group[COL_COMMITTED_EXPOSURE].sum(),
                     COL_TOTAL_DRAWN: drawn, COL_TOTAL_EAD: ead,
                     COL_WEIGHTED_PD: (group[COL_LIFETIME_PD] * group[COL_EAD]).sum() / ead,
                     COL_WEIGHTED_LGD: (group[COL_LGD] * group[COL_EAD]).sum() / ead,
                     COL_BASE_RESERVE: group[COL_BASE_LIFETIME_LOSS].sum(), COL_QUALITATIVE_OVERLAY: group[COL_QUALITATIVE_OVERLAY].sum(),
                     COL_TOTAL_ACL: acl, COL_ACL_COVERAGE: acl / drawn * 100})
    cohorts = pd.DataFrame(rows)
    cohorts.to_csv(CECL_COHORT_PATH, index=False)
    ending = round(tape[COL_TOTAL_RESERVE].sum(), 2)
    beginning = round(ending * BEGINNING_ACL_FACTOR, 2)
    provision = round(ending - beginning + GROSS_CHARGE_OFFS - RECOVERIES, 2)
    # Ending stock components are disclosures, not provision components.
    components = [("Beginning Allowance", beginning), ("Provision Expense", provision),
                  ("Ending Base Model Reserve (disclosure)", tape[COL_BASE_LIFETIME_LOSS].sum()),
                  ("Ending Qualitative Economic Overlay (disclosure)", tape[COL_QUALITATIVE_OVERLAY].sum()),
                  ("Gross Charge-offs", -GROSS_CHARGE_OFFS), ("Recoveries", RECOVERIES),
                  ("Net Charge-offs (subtotal)", RECOVERIES - GROSS_CHARGE_OFFS), ("Ending Allowance", ending)]
    roll = pd.DataFrame([{COL_LINE_ORDER: i, COL_COMPONENT: label, COL_AMOUNT: round(value, 2)} for i, (label, value) in enumerate(components, 1)])
    roll.to_csv(CECL_ROLL_FORWARD_PATH, index=False)
    summary = pd.DataFrame([{COL_METRIC_NAME: label, COL_METRIC_VALUE: value} for label, value in [
        ("Total EAD ($)", tape[COL_EAD].sum()), ("Base reserve ($)", tape[COL_BASE_LIFETIME_LOSS].sum()),
        ("Overlay ($)", tape[COL_QUALITATIVE_OVERLAY].sum()), ("Ending ACL ($)", ending),
        ("Coverage on drawn (%)", ending / tape[COL_DRAWN_BALANCE].sum() * 100)]])
    summary.to_csv(CECL_SUMMARY_PATH, index=False)
    print("SYNTHETIC CECL results:\n" + summary.to_string(index=False))
    return tape, roll, cohorts

if __name__ == "__main__":
    compute_cecl_portfolio_reserves()
