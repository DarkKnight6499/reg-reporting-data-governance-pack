import os
import sys
import pandas as pd

# CONFIG
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from python.config import *

DICTIONARY_ENTRIES = [
        {
            COL_DICT_LINE_ITEM: "Item 1",
            COL_DICT_FIELD_NAME: COL_BORROWER_ID,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "VARCHAR(32)",
            COL_DICT_DEFINITION: "Unique internal identifier for the obligor or corporate borrower.",
            COL_DICT_ALLOWED_VALUES: "Internal entity identifier string (e.g. BORR_00001).",
            COL_DICT_CDE_FLAG: "Y",
            COL_DICT_INSTRUCTIONS: "Report primary obligor code assigned in loan origination system."
        },
        {
            COL_DICT_LINE_ITEM: "Item 2",
            COL_DICT_FIELD_NAME: COL_BORROWER_LEI,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "CHAR(20)",
            COL_DICT_DEFINITION: "Synthetic 20-character obligor identifier; checksum not validated.",
            COL_DICT_ALLOWED_VALUES: "20-character alphanumeric synthetic string; required in this demonstration.",
            COL_DICT_CDE_FLAG: "Y",
            COL_DICT_INSTRUCTIONS: "Project assumption: require populated synthetic identifier."
        },
        {
            COL_DICT_LINE_ITEM: "Item 3",
            COL_DICT_FIELD_NAME: COL_BORROWER_NAME,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "VARCHAR(120)",
            COL_DICT_DEFINITION: "Legal registered business name of the corporate borrower.",
            COL_DICT_ALLOWED_VALUES: "Full registered corporate name.",
            COL_DICT_CDE_FLAG: "N",
            COL_DICT_INSTRUCTIONS: "Report corporate name exactly as recorded in legal credit agreement."
        },
        {
            COL_DICT_LINE_ITEM: "Item 4",
            COL_DICT_FIELD_NAME: COL_INDUSTRY_NAICS,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "CHAR(4)",
            COL_DICT_DEFINITION: "Four-digit North American Industry Classification System code.",
            COL_DICT_ALLOWED_VALUES: "One of ten configured industry labels; classification not externally validated.",
            COL_DICT_CDE_FLAG: "Y",
            COL_DICT_INSTRUCTIONS: "Reflect the primary line of business generating borrower cash flows."
        },
        {
            COL_DICT_LINE_ITEM: "Item 5",
            COL_DICT_FIELD_NAME: COL_FACILITY_ID,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "VARCHAR(32)",
            COL_DICT_DEFINITION: "Unique internal credit facility identifier assigned in loan accounting system.",
            COL_DICT_ALLOWED_VALUES: "Alphanumeric facility identifier (e.g. FAC_00001).",
            COL_DICT_CDE_FLAG: "Y",
            COL_DICT_INSTRUCTIONS: "Must remain constant across reporting quarters for tracking."
        },
        {
            COL_DICT_LINE_ITEM: "Item 6",
            COL_DICT_FIELD_NAME: COL_FACILITY_TYPE,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "VARCHAR(32)",
            COL_DICT_DEFINITION: "Type of loan credit facility committed by reporting institution.",
            COL_DICT_ALLOWED_VALUES: "Term Loan, Revolving Credit, Letter of Credit, Bridge Loan.",
            COL_DICT_CDE_FLAG: "Y",
            COL_DICT_INSTRUCTIONS: "Classify based on credit agreement terms and liquidity structure."
        },
        {
            COL_DICT_LINE_ITEM: "Item 7",
            COL_DICT_FIELD_NAME: COL_COMMITTED_EXPOSURE,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "DECIMAL(18,2)",
            COL_DICT_DEFINITION: "Total legally committed credit exposure in reporting currency.",
            COL_DICT_ALLOWED_VALUES: "Positive numeric currency amount >= Drawn Balance.",
            COL_DICT_CDE_FLAG: "Y",
            COL_DICT_INSTRUCTIONS: "Report total facility commitment including drawn and undrawn amounts."
        },
        {
            COL_DICT_LINE_ITEM: "Item 8",
            COL_DICT_FIELD_NAME: COL_UTILIZED_EXPOSURE,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "DECIMAL(18,2)",
            COL_DICT_DEFINITION: "Total utilized or drawn outstanding credit balance.",
            COL_DICT_ALLOWED_VALUES: "Non-negative numeric currency amount <= Committed Exposure.",
            COL_DICT_CDE_FLAG: "Y",
            COL_DICT_INSTRUCTIONS: "Report outstanding principal balance net of charge-offs."
        },
        {
            COL_DICT_LINE_ITEM: "Item 9",
            COL_DICT_FIELD_NAME: COL_UTILIZATION_RATE,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "DECIMAL(5,4)",
            COL_DICT_DEFINITION: "Ratio of utilized exposure to total committed credit facility.",
            COL_DICT_ALLOWED_VALUES: "Numeric fraction between 0.0000 and 1.0000.",
            COL_DICT_CDE_FLAG: "N",
            COL_DICT_INSTRUCTIONS: "Computed as Utilized Exposure divided by Committed Exposure."
        },
        {
            COL_DICT_LINE_ITEM: "Item 10",
            COL_DICT_FIELD_NAME: COL_RISK_RATING,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "INTEGER",
            COL_DICT_DEFINITION: "Internal obligor credit risk rating grade on institutional 8-point scale.",
            COL_DICT_ALLOWED_VALUES: "Integer from 1 (Minimal Risk) to 8 (Loss).",
            COL_DICT_CDE_FLAG: "Y",
            COL_DICT_INSTRUCTIONS: "Reflect current approved internal borrower risk rating."
        },
        {
            COL_DICT_LINE_ITEM: "Item 11",
            COL_DICT_FIELD_NAME: COL_RATING_GRADE_DESC,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "VARCHAR(32)",
            COL_DICT_DEFINITION: "Descriptive classification of internal credit rating grade.",
            COL_DICT_ALLOWED_VALUES: "Minimal Risk, Modest Risk, Average Risk, Acceptable Risk, Special Mention, Substandard, Doubtful, Loss.",
            COL_DICT_CDE_FLAG: "N",
            COL_DICT_INSTRUCTIONS: "Use the configured synthetic internal grade description."
        },
        {
            COL_DICT_LINE_ITEM: "Item 12",
            COL_DICT_FIELD_NAME: COL_COLLATERAL_ID,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "VARCHAR(32)",
            COL_DICT_DEFINITION: "Unique collateral record identifier linked to facility.",
            COL_DICT_ALLOWED_VALUES: "Alphanumeric collateral identifier (e.g. COL_00001).",
            COL_DICT_CDE_FLAG: "N",
            COL_DICT_INSTRUCTIONS: "Foreign key linking facility to collateral management database."
        },
        {
            COL_DICT_LINE_ITEM: "Item 13",
            COL_DICT_FIELD_NAME: COL_COLLATERAL_TYPE,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "VARCHAR(40)",
            COL_DICT_DEFINITION: "Primary category of collateral securing credit facility.",
            COL_DICT_ALLOWED_VALUES: "Commercial Real Estate, Equipment and Machinery, Accounts Receivable and Inventory, Cash and Marketable Securities, Unsecured.",
            COL_DICT_CDE_FLAG: "Y",
            COL_DICT_INSTRUCTIONS: "Select primary asset class pledged as perfected security interest."
        },
        {
            COL_DICT_LINE_ITEM: "Item 14",
            COL_DICT_FIELD_NAME: COL_COLLATERAL_VALUE,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "DECIMAL(18,2)",
            COL_DICT_DEFINITION: "Appraised current market valuation of pledged collateral assets.",
            COL_DICT_ALLOWED_VALUES: "Non-negative numeric amount. Zero for unsecured.",
            COL_DICT_CDE_FLAG: "Y",
            COL_DICT_INSTRUCTIONS: "Report latest independent appraisal or marked collateral value."
        },
        {
            COL_DICT_LINE_ITEM: "Item 15",
            COL_DICT_FIELD_NAME: COL_ORIGINATION_DATE,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "DATE",
            COL_DICT_DEFINITION: "Date on which credit facility agreement legally took effect.",
            COL_DICT_ALLOWED_VALUES: "Valid calendar date in YYYY-MM-DD format.",
            COL_DICT_CDE_FLAG: "N",
            COL_DICT_INSTRUCTIONS: "Must precede or equal current reporting period date."
        },
        {
            COL_DICT_LINE_ITEM: "Item 16",
            COL_DICT_FIELD_NAME: COL_MATURITY_DATE,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "DATE",
            COL_DICT_DEFINITION: "Current legal expiration or contractual maturity date of facility.",
            COL_DICT_ALLOWED_VALUES: "Valid calendar date in YYYY-MM-DD format >= Origination Date.",
            COL_DICT_CDE_FLAG: "Y",
            COL_DICT_INSTRUCTIONS: "Reflect legal maturity stated in operative credit amendment."
        },
        {
            COL_DICT_LINE_ITEM: "Item 17",
            COL_DICT_FIELD_NAME: COL_INTEREST_RATE,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "DECIMAL(6,4)",
            COL_DICT_DEFINITION: "Effective annualized nominal interest rate or spread applied.",
            COL_DICT_ALLOWED_VALUES: "Decimal rate between 0.0000 and 0.3000 (0% to 30%).",
            COL_DICT_CDE_FLAG: "N",
            COL_DICT_INSTRUCTIONS: "Reflect current all-in coupon rate applicable at quarter-end."
        },
        {
            COL_DICT_LINE_ITEM: "Item 18",
            COL_DICT_FIELD_NAME: COL_CURRENCY,
            COL_DICT_SCHEDULE: "SYNTHETIC H.1-style subset; project item numbering",
            COL_DICT_DATA_TYPE: "CHAR(3)",
            COL_DICT_DEFINITION: "ISO 4217 three-letter denomination currency code.",
            COL_DICT_ALLOWED_VALUES: "USD.",
            COL_DICT_CDE_FLAG: "N",
            COL_DICT_INSTRUCTIONS: "Denominate all reported exposures in base US Dollars."
        }
    ]

SCHEDULE_COLS = [
        COL_BORROWER_ID,
        COL_BORROWER_LEI,
        COL_BORROWER_NAME,
        COL_INDUSTRY_NAICS,
        COL_FACILITY_ID,
        COL_FACILITY_TYPE,
        COL_COMMITTED_EXPOSURE,
        COL_UTILIZED_EXPOSURE,
        COL_UTILIZATION_RATE,
        COL_RISK_RATING,
        COL_RATING_GRADE_DESC,
        COL_COLLATERAL_ID,
        COL_COLLATERAL_TYPE,
        COL_COLLATERAL_VALUE,
        COL_ORIGINATION_DATE,
        COL_MATURITY_DATE,
        COL_INTEREST_RATE,
        COL_CURRENCY
    ]

def build_field_dictionary():

    return pd.DataFrame(DICTIONARY_ENTRIES)

def build_fr_y14q_schedule():

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    
    tape_df = pd.read_csv(LOAN_TAPE_CLEAN_PATH, dtype={COL_BORROWER_LEI: str})

    schedule_df = tape_df[SCHEDULE_COLS].copy()

    schedule_df.to_csv(FR_Y14Q_SCHEDULE_DATA_PATH, index=False)
    schedule_df.to_csv(FR_Y14Q_SCHEDULE_OUTPUT_PATH, index=False)
    
    dict_df = build_field_dictionary()
    dict_df.to_csv(FR_Y14Q_DICT_PATH, index=False)
    
    tot_committed = schedule_df[COL_COMMITTED_EXPOSURE].sum()
    tot_utilized = schedule_df[COL_UTILIZED_EXPOSURE].sum()
    tot_collateral = schedule_df[COL_COLLATERAL_VALUE].sum()
    
    print("FR Y-14Q Schedule H.1 Corporate Loan Schedule Built:")
    print(f"Total Reporting Facilities: {len(schedule_df):,}")
    print(f"Total Committed Exposure:   ${tot_committed:,.2f}")
    print(f"Total Utilized Exposure:    ${tot_utilized:,.2f}")
    print(f"Total Collateral Valuation: ${tot_collateral:,.2f}")
    print(f"Schedule written to:        {FR_Y14Q_SCHEDULE_OUTPUT_PATH}")
    print(f"Field dictionary written:   {FR_Y14Q_DICT_PATH}")
    
    return schedule_df, dict_df

if __name__ == "__main__":
    build_fr_y14q_schedule()
