import os
import sys
import pandas as pd

# CONFIG
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from python.config import *

CHART_DQ_PATH = os.path.join(OUTPUTS_DIR, "dq_rule_pass_rates.png")
CHART_AGING_PATH = os.path.join(OUTPUTS_DIR, "dq_issue_aging_distribution.png")
CHART_CECL_PATH = os.path.join(OUTPUTS_DIR, "cecl_reserve_by_tier.png")
CHART_DPI = 150
CHART_DQ_SIZE = (10, 5)
CHART_AGING_SIZE = (8, 5)
CHART_CECL_SIZE = (9, 5)
CHART_DQ_LIMITS = (0, 101)
CHART_COLORS = ("#2b5c8f", "#d9534f", "#337ab7", "#1b4965", "#62b6cb")

def generate_visual_charts():

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib not detected: skipping chart generation.")
        return False
        
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    if os.path.exists(DQ_RESULTS_PATH):
        dq_df = pd.read_csv(DQ_RESULTS_PATH)
        plt.figure(figsize=CHART_DQ_SIZE)
        plt.barh(dq_df[COL_DQ_RULE_ID], dq_df[COL_PASS_RATE_PCT], color=CHART_COLORS[0])
        plt.axvline(100.0, color=CHART_COLORS[1], linestyle="dashed", linewidth=1.5)
        plt.xlabel("Pass Rate (%)")
        plt.title("SYNTHETIC: Data Quality Rule Pass Rates on Injected Defect Benchmark")
        plt.xlim(*CHART_DQ_LIMITS)
        plt.tight_layout()
        chart1_path = CHART_DQ_PATH
        plt.savefig(chart1_path, dpi=CHART_DPI, metadata={"Author": CHART_AUTHOR})
        plt.close()
        print(f"Chart saved: {chart1_path}")

    if os.path.exists(DQ_AGING_PATH):
        aging_df = pd.read_csv(DQ_AGING_PATH)
        filtered_aging = aging_df[~aging_df[COL_AGE_BUCKET].str.contains("TOTAL|CLOSED")]
        if not filtered_aging.empty:
            plt.figure(figsize=CHART_AGING_SIZE)
            plt.bar(filtered_aging[COL_AGE_BUCKET], filtered_aging[COL_OPEN_COUNT], color=CHART_COLORS[2])
            plt.xlabel("Aging Category")
            plt.ylabel("Open Issue Count")
            plt.title("SYNTHETIC: Data Quality Issue Aging Distribution")
            plt.tight_layout()
            chart2_path = CHART_AGING_PATH
            plt.savefig(chart2_path, dpi=CHART_DPI, metadata={"Author": CHART_AUTHOR})
            plt.close()
            print(f"Chart saved: {chart2_path}")

    if os.path.exists(CECL_COHORT_PATH):
        cohort_df = pd.read_csv(CECL_COHORT_PATH)
        tier_agg = cohort_df.groupby(COL_RATING_TIER).agg(
            base_reserve=(COL_BASE_RESERVE, "sum"),
            qualitative_overlay=(COL_QUALITATIVE_OVERLAY, "sum")
        ).reset_index()
        
        plt.figure(figsize=CHART_CECL_SIZE)
        x = range(len(tier_agg))
        plt.bar(x, tier_agg[COL_BASE_RESERVE] / 1e6, label="Base Quantitative CECL ($M)", color=CHART_COLORS[3])
        plt.bar(x, tier_agg[COL_QUALITATIVE_OVERLAY] / 1e6, bottom=tier_agg[COL_BASE_RESERVE] / 1e6, label="Qualitative Overlay ($M)", color=CHART_COLORS[4])
        plt.xticks(x, tier_agg[COL_RATING_TIER])
        plt.ylabel("Reserve Amount ($ Millions)")
        plt.title("SYNTHETIC: CECL Allowance for Credit Losses by Supervisory Tier")
        plt.legend()
        plt.tight_layout()
        chart3_path = CHART_CECL_PATH
        plt.savefig(chart3_path, dpi=CHART_DPI, metadata={"Author": CHART_AUTHOR})
        plt.close()
        print(f"Chart saved: {chart3_path}")
        
    return True

if __name__ == "__main__":
    generate_visual_charts()
