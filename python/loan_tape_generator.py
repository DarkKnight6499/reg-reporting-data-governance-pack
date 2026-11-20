import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# CONFIG
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from python.config import *

def build_synthetic_borrower_directory(borrower_count, rng):

    borrowers = []
    for i in range(1, borrower_count + 1):
        b_id = f"BORR_{i:05d}"
        prefix = rng.choice(PREFIXES)
        suffix = rng.choice(SUFFIXES)
        legal = rng.choice(LEGAL_FORMS)
        name = f"{prefix} {suffix} {legal} #{i}"

        lei_prefix = f"{LEI_SYNTHETIC_PREFIX}{i:04d}"
        lei_suffix = f"{rng.integers(*LEI_SUFFIX_RANGE)}{LEI_SYNTHETIC_SUFFIX}"
        lei = f"{lei_prefix}{lei_suffix}"[:LEI_LENGTH]
        
        sec_idx = rng.integers(0, len(SECTORS))
        naics, industry = SECTORS[sec_idx]
        
        borrowers.append({
            COL_BORROWER_ID: b_id,
            COL_BORROWER_NAME: name,
            COL_BORROWER_LEI: lei,
            COL_INDUSTRY_NAICS: naics,
            COL_INDUSTRY_NAME: industry
        })
        
    return pd.DataFrame(borrowers)

def generate_clean_loan_tape(loan_count=TOTAL_LOAN_COUNT, seed=RANDOM_SEED):

    rng = np.random.default_rng(seed)
    borrowers_df = build_synthetic_borrower_directory(TOTAL_BORROWER_COUNT, rng)

    records = []
    reporting_dt = datetime.strptime(REPORTING_DATE, DATE_FORMAT)

    borrower_indices = rng.integers(0, len(borrowers_df), size=loan_count)
    
    for i in range(loan_count):
        fac_num = i + 1
        fac_id = f"FAC_{fac_num:05d}"
        col_id = f"COL_{fac_num:05d}"
        
        borrower_row = borrowers_df.loc[borrower_indices[i]]
        b_id = borrower_row[COL_BORROWER_ID]
        b_name = borrower_row[COL_BORROWER_NAME]
        b_lei = borrower_row[COL_BORROWER_LEI]
        naics = borrower_row[COL_INDUSTRY_NAICS]
        industry = borrower_row[COL_INDUSTRY_NAME]
        
        fac_type = rng.choice(FACILITY_TYPES, p=FACILITY_WEIGHTS)
        col_type = rng.choice(COLLATERAL_TYPES, p=COLLATERAL_WEIGHTS)
        rating = int(rng.choice(RATING_GRADES, p=RATING_WEIGHTS))
        rating_desc = RATING_DESCRIPTIONS[rating]

        raw_commitment = float(np.exp(rng.normal(*COMMITMENT_LOGNORMAL)))
        committed = float(np.clip(raw_commitment, *COMMITMENT_LIMITS))
        committed = round(committed, MONEY_DECIMALS)

        if fac_type == "Term Loan":
            util_rate = float(rng.uniform(*TERM_UTILIZATION))
        elif fac_type == "Revolving Credit":
            util_rate = float(rng.uniform(*REVOLVER_UTILIZATION))
        elif fac_type == "Letter of Credit":
            util_rate = float(rng.uniform(*LOC_UTILIZATION))
        else:
            util_rate = FULL_UTILIZATION
            
        drawn = round(committed * util_rate, MONEY_DECIMALS)
        undrawn = round(committed - drawn, MONEY_DECIMALS)
        util_rate_calc = round(drawn / committed, RATIO_DECIMALS)

        if col_type == "Unsecured":
            collateral_val = ZERO_COLLATERAL
        elif col_type == "Cash and Marketable Securities":
            collateral_val = round(committed * float(rng.uniform(*CASH_COVERAGE)), MONEY_DECIMALS)
        elif col_type == "Commercial Real Estate":
            collateral_val = round(committed * float(rng.uniform(*CRE_COVERAGE)), MONEY_DECIMALS)
        elif col_type == "Equipment and Machinery":
            collateral_val = round(committed * float(rng.uniform(*EQUIPMENT_COVERAGE)), MONEY_DECIMALS)
        else:
            collateral_val = round(committed * float(rng.uniform(*OTHER_COVERAGE)), MONEY_DECIMALS)

        orig_days_ago = int(rng.integers(*ORIGINATION_DAYS_RANGE))
        orig_dt = reporting_dt - timedelta(days=orig_days_ago)
        mat_days_ahead = int(rng.integers(*MATURITY_DAYS_RANGE))
        mat_dt = reporting_dt + timedelta(days=mat_days_ahead)
        
        orig_str = orig_dt.strftime(DATE_FORMAT)
        mat_str = mat_dt.strftime(DATE_FORMAT)

        base_rate = SYNTHETIC_BASE_RATE
        spread = SPREAD_BASE + (rating * SPREAD_RATING_STEP) + float(rng.uniform(*SPREAD_NOISE))
        interest_rate = round(base_rate + spread, RATIO_DECIMALS)
        
        records.append({
            COL_BORROWER_ID: b_id,
            COL_BORROWER_NAME: b_name,
            COL_BORROWER_LEI: b_lei,
            COL_INDUSTRY_NAICS: naics,
            COL_INDUSTRY_NAME: industry,
            COL_FACILITY_ID: fac_id,
            COL_FACILITY_TYPE: fac_type,
            COL_COMMITTED_EXPOSURE: committed,
            COL_UTILIZED_EXPOSURE: drawn,
            COL_DRAWN_BALANCE: drawn,
            COL_UNDRAWN_COMMITMENT: undrawn,
            COL_UTILIZATION_RATE: util_rate_calc,
            COL_RISK_RATING: rating,
            COL_RATING_GRADE_DESC: rating_desc,
            COL_COLLATERAL_ID: col_id,
            COL_COLLATERAL_TYPE: col_type,
            COL_COLLATERAL_VALUE: collateral_val,
            COL_ORIGINATION_DATE: orig_str,
            COL_MATURITY_DATE: mat_str,
            COL_INTEREST_RATE: interest_rate,
            COL_CURRENCY: BASE_CURRENCY,
            COL_IS_DEFECTIVE: False,
            COL_DEFECT_TYPE: "None"
        })
        
    df = pd.DataFrame(records)
    return df

def inject_controlled_defects(clean_df, seed=RANDOM_SEED):

    defect_df = clean_df.copy()
    rng = np.random.default_rng(seed + DEFECT_SEED_OFFSET)

    idx_lei = rng.choice(defect_df.index, size=DEFECT_LEI_COUNT, replace=False)
    defect_df.loc[idx_lei, COL_BORROWER_LEI] = ""
    defect_df.loc[idx_lei, COL_IS_DEFECTIVE] = True
    defect_df.loc[idx_lei, COL_DEFECT_TYPE] = "Missing Borrower LEI"

    remaining_1 = defect_df[~defect_df[COL_IS_DEFECTIVE]].index
    idx_rating = rng.choice(remaining_1, size=DEFECT_STANDARD_COUNT, replace=False)
    defect_df.loc[idx_rating, COL_RISK_RATING] = DEFECT_INVALID_RATING
    defect_df.loc[idx_rating, COL_RATING_GRADE_DESC] = "Invalid Out of Scope Rating"
    defect_df.loc[idx_rating, COL_IS_DEFECTIVE] = True
    defect_df.loc[idx_rating, COL_DEFECT_TYPE] = "Invalid Risk Rating Out of Bounds"

    remaining_2 = defect_df[~defect_df[COL_IS_DEFECTIVE]].index
    idx_col = rng.choice(remaining_2, size=DEFECT_STANDARD_COUNT, replace=False)
    defect_df.loc[idx_col, COL_COLLATERAL_VALUE] = DEFECT_COLLATERAL_VALUE
    defect_df.loc[idx_col, COL_IS_DEFECTIVE] = True
    defect_df.loc[idx_col, COL_DEFECT_TYPE] = "Negative Collateral Valuation"

    remaining_3 = defect_df[~defect_df[COL_IS_DEFECTIVE]].index
    idx_overdrawn = rng.choice(remaining_3, size=DEFECT_STANDARD_COUNT, replace=False)
    defect_df.loc[idx_overdrawn, COL_DRAWN_BALANCE] = (
        defect_df.loc[idx_overdrawn, COL_COMMITTED_EXPOSURE] + DEFECT_OVERDRAWN_AMOUNT
    )
    defect_df.loc[idx_overdrawn, COL_UTILIZED_EXPOSURE] = defect_df.loc[idx_overdrawn, COL_DRAWN_BALANCE]
    defect_df.loc[idx_overdrawn, COL_UTILIZATION_RATE] = round(
        defect_df.loc[idx_overdrawn, COL_DRAWN_BALANCE] / defect_df.loc[idx_overdrawn, COL_COMMITTED_EXPOSURE], 4
    )
    defect_df.loc[idx_overdrawn, COL_IS_DEFECTIVE] = True
    defect_df.loc[idx_overdrawn, COL_DEFECT_TYPE] = "Drawn Balance Exceeds Committed Exposure"

    remaining_4 = defect_df[~defect_df[COL_IS_DEFECTIVE]].index
    idx_dates = rng.choice(remaining_4, size=DEFECT_STANDARD_COUNT, replace=False)
    defect_df.loc[idx_dates, COL_MATURITY_DATE] = DEFECT_MATURITY_DATE
    defect_df.loc[idx_dates, COL_IS_DEFECTIVE] = True
    defect_df.loc[idx_dates, COL_DEFECT_TYPE] = "Maturity Date Precedes Origination Date"

    remaining_5 = defect_df[~defect_df[COL_IS_DEFECTIVE]].index
    idx_orphan = rng.choice(remaining_5, size=DEFECT_BORROWER_COUNT, replace=False)
    defect_df.loc[idx_orphan, COL_BORROWER_ID] = ""
    defect_df.loc[idx_orphan, COL_IS_DEFECTIVE] = True
    defect_df.loc[idx_orphan, COL_DEFECT_TYPE] = "Orphaned Facility Missing Borrower ID"
    
    return defect_df

def save_generated_datasets():

    os.makedirs(DATA_DIR, exist_ok=True)
    
    clean_df = generate_clean_loan_tape(TOTAL_LOAN_COUNT, RANDOM_SEED)
    clean_df.to_csv(LOAN_TAPE_CLEAN_PATH, index=False)
    
    defects_df = inject_controlled_defects(clean_df, RANDOM_SEED)
    defects_df.to_csv(LOAN_TAPE_DEFECTS_PATH, index=False)
    
    total_committed = clean_df[COL_COMMITTED_EXPOSURE].sum()
    total_drawn = clean_df[COL_DRAWN_BALANCE].sum()
    total_collateral = clean_df[COL_COLLATERAL_VALUE].sum()
    defect_count = defects_df[COL_IS_DEFECTIVE].sum()
    
    print("Wholesale Loan Tape Generation Complete:")
    print(f"Total Facilities Generated: {len(clean_df):,}")
    print(f"Total Committed Exposure:   ${total_committed:,.2f}")
    print(f"Total Drawn Balance:        ${total_drawn:,.2f}")
    print(f"Total Collateral Valuation: ${total_collateral:,.2f}")
    print(f"Controlled Defects Injected:{defect_count:,} records in testing tape")
    
    return clean_df, defects_df

if __name__ == "__main__":
    save_generated_datasets()
