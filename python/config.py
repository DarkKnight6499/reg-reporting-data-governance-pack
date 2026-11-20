import os

# CONFIG
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
TESTS_DIR = os.path.join(BASE_DIR, "tests")

LOAN_TAPE_CLEAN_PATH = os.path.join(DATA_DIR, "synthetic_wholesale_loan_tape.csv")
LOAN_TAPE_DEFECTS_PATH = os.path.join(DATA_DIR, "synthetic_loan_tape_with_defects.csv")
FR_Y14Q_SCHEDULE_DATA_PATH = os.path.join(DATA_DIR, "fr_y14q_corporate_loan_schedule.csv")
FR_Y14Q_SCHEDULE_OUTPUT_PATH = os.path.join(OUTPUTS_DIR, "fr_y14q_schedule_h1.csv")
FR_Y14Q_DICT_PATH = os.path.join(OUTPUTS_DIR, "fr_y14q_field_dictionary.csv")
CECL_SUMMARY_PATH = os.path.join(OUTPUTS_DIR, "cecl_reserve_summary.csv")
CECL_ROLL_FORWARD_PATH = os.path.join(OUTPUTS_DIR, "cecl_roll_forward.csv")
CECL_COHORT_PATH = os.path.join(OUTPUTS_DIR, "cecl_cohort_analysis.csv")
METADATA_CATALOG_PATH = os.path.join(OUTPUTS_DIR, "metadata_catalog_cde.csv")
DQ_RESULTS_PATH = os.path.join(OUTPUTS_DIR, "dq_rule_results.csv")
DQ_AGING_PATH = os.path.join(OUTPUTS_DIR, "dq_issue_aging_kpis.csv")
BCBS_ASSESSMENT_PATH = os.path.join(OUTPUTS_DIR, "bcbs_239_compliance_assessment.csv")
RECON_BREAKS_PATH = os.path.join(OUTPUTS_DIR, "reconciliation_breaks_fr2052a_vs_gl.csv")
RECON_SUMMARY_PATH = os.path.join(OUTPUTS_DIR, "reconciliation_summary.csv")
MEMO_PATH = os.path.join(OUTPUTS_DIR, "regulatory_data_governance_memo.md")

RANDOM_SEED = 42
TOTAL_LOAN_COUNT = 5000
TOTAL_BORROWER_COUNT = 3800
REPORTING_DATE = "2024-09-30"

COL_BORROWER_ID = "borrower_id"
COL_BORROWER_NAME = "borrower_name"
COL_BORROWER_LEI = "borrower_lei"
COL_INDUSTRY_NAICS = "industry_naics"
COL_INDUSTRY_NAME = "industry_name"
COL_FACILITY_ID = "facility_id"
COL_FACILITY_TYPE = "facility_type"
COL_COMMITTED_EXPOSURE = "committed_exposure"
COL_UTILIZED_EXPOSURE = "utilized_exposure"
COL_DRAWN_BALANCE = "drawn_balance"
COL_UNDRAWN_COMMITMENT = "undrawn_commitment"
COL_UTILIZATION_RATE = "utilization_rate"
COL_RISK_RATING = "risk_rating"
COL_RATING_GRADE_DESC = "rating_grade_desc"
COL_COLLATERAL_ID = "collateral_id"
COL_COLLATERAL_TYPE = "collateral_type"
COL_COLLATERAL_VALUE = "collateral_value"
COL_ORIGINATION_DATE = "origination_date"
COL_MATURITY_DATE = "maturity_date"
COL_INTEREST_RATE = "interest_rate"
COL_CURRENCY = "currency"
COL_IS_DEFECTIVE = "is_defective"
COL_DEFECT_TYPE = "defect_type"

COL_FIELD_NAME = "field_name"
COL_FIELD_DESCRIPTION = "field_description"
COL_DATA_STEWARD = "data_steward"
COL_CDE_FLAG = "cde_flag"
COL_SOURCE_SYSTEM = "source_system"
COL_LINEAGE_HOPS = "lineage_hops"
COL_DQ_RULE_ID = "dq_rule_id"
COL_DQ_DIMENSION = "dq_dimension"
COL_DQ_RULE_DESC = "dq_rule_description"
COL_TOTAL_RECORDS = "total_records"
COL_PASS_COUNT = "pass_count"
COL_FAIL_COUNT = "fail_count"
COL_PASS_RATE_PCT = "pass_rate_pct"

COL_ISSUE_ID = "issue_id"
COL_ISSUE_SEVERITY = "issue_severity"
COL_AGE_BUCKET = "age_bucket"
COL_AGE_DAYS = "age_days"
COL_ISSUE_STATUS = "issue_status"
COL_REMEDIATION_OWNER = "remediation_owner"

COL_EAD = "exposure_at_default"
COL_LIFETIME_PD = "lifetime_pd"
COL_LGD = "loss_given_default"
COL_BASE_LIFETIME_LOSS = "base_lifetime_loss"
COL_QUALITATIVE_OVERLAY = "qualitative_overlay"
COL_TOTAL_RESERVE = "total_reserve"
COL_TENOR_YEARS = "tenor_years"
COL_RATING_TIER = "rating_tier"

COL_PRINCIPLE_NUM = "principle_number"
COL_PRINCIPLE_NAME = "principle_name"
COL_BCBS_CATEGORY = "category"
COL_EVIDENCE = "evidence"
COL_GAP = "gap"
COL_SCORE_0_TO_3 = "score_0_to_3"
COL_SCORE_RATIONALE = "score_rationale"

COL_RECON_ID = "recon_id"
COL_PRODUCT_DESC = "product_description"
COL_SCHEDULE_AMOUNT = "schedule_amount"
COL_GL_AMOUNT = "gl_amount"
COL_VARIANCE_AMOUNT = "variance_amount"
COL_VARIANCE_PCT = "variance_pct"
COL_BREAK_FLAG = "break_flag"
COL_ROOT_CAUSE_TAG = "root_cause_tag"
COL_BREAK_AGE_DAYS = "break_age_days"
COL_BREAK_AGE_BUCKET = "break_age_bucket"

RECON_TOLERANCE_DOLLARS = 10000.0
RECON_TOLERANCE_PCT = 0.0005
RECON_IMMATERIAL_THRESHOLD = 100.0

RATING_DESCRIPTIONS = {
    1: "Minimal Risk",
    2: "Modest Risk",
    3: "Average Risk",
    4: "Acceptable Risk",
    5: "Special Mention",
    6: "Substandard",
    7: "Doubtful",
    8: "Loss"
}

RATING_ANNUAL_PD = {
    1: 0.0008,
    2: 0.0020,
    3: 0.0055,
    4: 0.0140,
    5: 0.0350,
    6: 0.0850,
    7: 0.2200,
    8: 0.6500
}

COLLATERAL_LGD = {
    "Cash and Marketable Securities": 0.10,
    "Commercial Real Estate": 0.25,
    "Equipment and Machinery": 0.35,
    "Accounts Receivable and Inventory": 0.42,
    "Unsecured": 0.50
}

CREDIT_CONVERSION_FACTOR = {
    "Term Loan": 0.00,
    "Revolving Credit": 0.50,
    "Letter of Credit": 0.20,
    "Bridge Loan": 1.00
}

CECL_FACILITY_PATH = os.path.join(OUTPUTS_DIR, "synthetic_cecl_facility_inputs.csv")
DQ_CLEAN_RESULTS_PATH = os.path.join(OUTPUTS_DIR, "dq_clean_rule_results.csv")
DQ_DETAIL_PATH = os.path.join(OUTPUTS_DIR, "dq_record_failures.csv")
DQ_ISSUES_PATH = os.path.join(OUTPUTS_DIR, "synthetic_issue_inventory.csv")
DQ_CLOSED_PATH = os.path.join(OUTPUTS_DIR, "synthetic_closed_issues.csv")
RECON_SCHEDULE_PATH = os.path.join(DATA_DIR, "synthetic_fr2052a_style_outflows.csv")
RECON_GL_PATH = os.path.join(DATA_DIR, "synthetic_gl.csv")
COL_TENOR_BUCKET = "tenor_bucket"
COL_ANNUAL_PD = "annual_pd"
COL_FACILITY_COUNT = "facility_count"
COL_TOTAL_COMMITTED = "total_committed"
COL_TOTAL_DRAWN = "total_drawn"
COL_TOTAL_EAD = "total_ead"
COL_WEIGHTED_PD = "weighted_pd"
COL_WEIGHTED_LGD = "weighted_lgd"
COL_BASE_RESERVE = "base_reserve"
COL_TOTAL_ACL = "total_acl"
COL_ACL_COVERAGE = "acl_coverage_drawn_pct"
COL_LINE_ORDER = "line_item_order"
COL_COMPONENT = "component_name"
COL_AMOUNT = "amount_usd"
COL_METRIC_NAME = "metric_name"
COL_METRIC_VALUE = "metric_value"
COL_SUMMARY_METRIC = "summary_metric"
COL_NARRATIVE = "narrative"
COL_OPEN_COUNT = "open_issues_count"
COL_AVG_AGE = "avg_age_days"
COL_MAX_AGE = "max_age_days"
COL_PCT_OPEN = "pct_of_total_open"
COL_CLOSE_DAYS = "days_to_close"
COL_DICT_FIELD_NAME = COL_FIELD_NAME
COL_DICT_SCHEDULE = "schedule_name"
COL_DICT_LINE_ITEM = "line_item_number"
COL_DICT_DATA_TYPE = "data_type"
COL_DICT_DEFINITION = "business_definition"
COL_DICT_ALLOWED_VALUES = "allowable_values"
COL_DICT_CDE_FLAG = "critical_data_element_flag"
COL_DICT_INSTRUCTIONS = "reporting_instructions"
MONEY_TOLERANCE = 0.01
DAYS_PER_YEAR = 365.25
TENOR_BREAKS = (2.0, 5.0)
CRITICIZED_RATING = 6
OVERLAY_BASE = 0.03
OVERLAY_CRE = 0.15
OVERLAY_CRITICIZED = 0.10
BEGINNING_ACL_FACTOR = 0.9425
GROSS_CHARGE_OFFS = 12450000.0
RECOVERIES = 2150000.0
ISSUE_SEED = 999
CLOSED_DURATIONS = [14, 18, 22, 26, 29, 34, 38, 42, 45, 52, 61, 68]
AGE_LIMITS = [30, 60, 90]
AGE_LABELS = ["0-30 Days", "31-60 Days", "61-90 Days", "91+ Days"]
ISSUE_AGE_RANGE = (5, 146)
RECON_AGE_LIMITS = (5, 15, 30)
RECON_SHOCKS = [2450000.0, -420000.0, 850000.0, -185000.0, 0.0, 42.50]
RECON_AGES = [3, 21, 38, 9, 0, 1]
RECON_CAUSES = ["Cutoff Timing Mismatch", "Manual Journal Entry", "Unmapped Facility Product Code", "Synthetic Valuation Adjustment", "Fully Reconciled", "Immaterial Rounding Noise"]
RECON_OWNERS = ["Credit Operations", "Financial Control", "Reporting Technology", "Treasury", "None", "Auto-Cleared"]
RECON_FEE_BALANCE = 45210.80
DQ_EXPECTED_FAILURES = {"DQ_COMP_01": 20, "DQ_COMP_02": 30, "DQ_COMP_03": 0, "DQ_VAL_01": 0, "DQ_VAL_02": 0, "DQ_VAL_03": 25, "DQ_RSN_01": 25, "DQ_RSN_02": 25, "DQ_RSN_03": 25, "DQ_REF_01": 0}
MEMO_PAGE_BREAK = '<div style="page-break-after: always;"></div>'

SECTORS = [
        ("3341", "Computer and Electronic Product Manufacturing"),
        ("3254", "Pharmaceutical and Medicine Manufacturing"),
        ("6221", "General Medical and Surgical Hospitals"),
        ("5182", "Data Processing and Hosting Services"),
        ("5311", "Lessors of Real Estate"),
        ("4841", "General Freight Trucking"),
        ("2111", "Oil and Gas Extraction"),
        ("4238", "Machinery and Equipment Merchant Wholesalers"),
        ("5415", "Computer Systems Design and Related Services"),
        ("2362", "Nonresidential Building Construction")
    ]

PREFIXES = [
        "Apex", "Summit", "Vanguard", "Pinnacle", "Meridian", "Cascade",
        "Pacific", "Atlantic", "Horizon", "Sterling", "Beacon", "Olympus",
        "Keystone", "Crestview", "Atlas", "Frontier", "Zenith", "Endeavor"
    ]

SUFFIXES = [
        "Industries", "Holdings", "Technologies", "Logistics", "Healthcare",
        "Capital", "Resources", "Manufacturing", "Energy", "Solutions"
    ]

LEGAL_FORMS = ["LLC", "Corp", "Inc", "LP"]

FACILITY_TYPES = ["Term Loan", "Revolving Credit", "Letter of Credit", "Bridge Loan"]

FACILITY_WEIGHTS = [0.50, 0.35, 0.10, 0.05]

COLLATERAL_TYPES = [
        "Commercial Real Estate",
        "Equipment and Machinery",
        "Accounts Receivable and Inventory",
        "Cash and Marketable Securities",
        "Unsecured"
    ]

COLLATERAL_WEIGHTS = [0.35, 0.25, 0.20, 0.10, 0.10]

RATING_GRADES = [1, 2, 3, 4, 5, 6, 7, 8]

RATING_WEIGHTS = [0.04, 0.10, 0.30, 0.32, 0.12, 0.07, 0.04, 0.01]

LEI_SUFFIX_RANGE = (10000000, 99999999)
COMMITMENT_LOGNORMAL = (15.2, 0.75)
COMMITMENT_LIMITS = (250000.0, 75000000.0)
TERM_UTILIZATION = (0.85, 1.00)
REVOLVER_UTILIZATION = (0.15, 0.90)
LOC_UTILIZATION = (0.00, 0.45)
CASH_COVERAGE = (1.10, 1.75)
CRE_COVERAGE = (0.90, 1.45)
EQUIPMENT_COVERAGE = (0.75, 1.25)
OTHER_COVERAGE = (0.65, 1.15)
ORIGINATION_DAYS_RANGE = (120, 2400)
MATURITY_DAYS_RANGE = (180, 3650)
SYNTHETIC_BASE_RATE = 0.0525
SPREAD_BASE = 0.0125
SPREAD_RATING_STEP = 0.0065
SPREAD_NOISE = (-0.0025, 0.0040)
DEFECT_SEED_OFFSET = 101
DEFECT_LEI_COUNT = 30
DEFECT_STANDARD_COUNT = 25
DEFECT_BORROWER_COUNT = 20
DEFECT_INVALID_RATING = 15
DEFECT_COLLATERAL_VALUE = -350000.0
DEFECT_OVERDRAWN_AMOUNT = 750000.0
DEFECT_MATURITY_DATE = "2015-01-15"
COL_MERGE_STATUS = "_merge"

LEI_LENGTH = 20
LEI_SYNTHETIC_PREFIX = "549300"
LEI_SYNTHETIC_SUFFIX = "89"
LEI_SHAPE_PATTERN = r"[A-Za-z0-9]{20}"
DATE_FORMAT = "%Y-%m-%d"
MONEY_DECIMALS = 2
RATIO_DECIMALS = 4
FULL_UTILIZATION = 1.0
ZERO_COLLATERAL = 0.0
BASE_CURRENCY = "USD"
CHART_AUTHOR = "Project Author"

UTILIZATION_TOLERANCE = 0.000051
INTEREST_RATE_LIMITS = (0.0, 0.30)
DQ_EXPECTED_FAILURES.update({"DQ_VAL_04": 0, "DQ_VAL_05": 0, "DQ_RSN_04": 25, "DQ_VAL_06": 25, "DQ_VAL_07": 0, "DQ_RSN_05": 0, "DQ_VAL_08": 0, "DQ_VAL_09": 0})
