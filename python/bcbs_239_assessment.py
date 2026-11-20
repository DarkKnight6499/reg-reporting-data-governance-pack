import os
import sys
import pandas as pd

# CONFIG
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT) if REPO_ROOT not in sys.path else None
from python.config import *
PRINCIPLE_ROWS = [
    ("Governance", "No organizational governance evidence in this repository.", "Board oversight, policy approval and independent accountability are absent.", 0),
    ("Data architecture and IT infrastructure", "config.py centralizes schema; run_all.py orchestrates local CSV processing.", "No resilience, enterprise integration or access-control demonstration.", 1),
    ("Accuracy and integrity", "Schedule tie-outs, ten DQ rules and reconciliation tests are executable.", "No independent source validation; only selected defects are tested.", 2),
    ("Completeness", "All 5,000 synthetic facilities and all 18 schedule fields are cataloged.", "No coverage of a real institution, entities or other products.", 2),
    ("Timeliness", "A single reporting snapshot is reproducible locally.", "No service-level monitoring or stress-period deadline evidence.", 1),
    ("Adaptability", "Credit mappings and tolerance inputs are configurable.", "No stress scenario engine or ad hoc request workflow.", 1),
    ("Accuracy", "CSV schedules tie to generated tape totals; reserve identities are tested.", "No independent report approval or filing validation.", 2),
    ("Comprehensiveness", "Pack covers exposure, collateral, credit loss and reconciliation examples.", "Only a narrow synthetic wholesale portfolio is represented.", 1),
    ("Clarity and usefulness", "Field dictionary and concise memo describe results and limits.", "No stakeholder usability evaluation.", 2),
    ("Frequency", "Manual reruns regenerate a single fixed snapshot.", "No scheduler or frequency controls.", 0),
    ("Distribution", "Artifacts are written to local folders.", "No authenticated distribution, recipient controls or audit trail.", 0),
]

def evaluate_bcbs_239_principles():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    rows = []
    for number, (name, evidence, gap, score) in enumerate(PRINCIPLE_ROWS, 1):
        rows.append({COL_PRINCIPLE_NUM: number, COL_PRINCIPLE_NAME: name, COL_BCBS_CATEGORY: "Illustrative project checklist",
                     COL_EVIDENCE: evidence, COL_GAP: gap, COL_SCORE_0_TO_3: score,
                     COL_SCORE_RATIONALE: f"Project evidence score {score}: 0 absent, 1 partial demonstration, 2 repeatable local controls, 3 independently validated operation. Not a compliance opinion."})
    assessment = pd.DataFrame(rows)
    assessment.to_csv(BCBS_ASSESSMENT_PATH, index=False)
    print(f"Illustrative BCBS 239 checklist: {len(assessment)} principles; project evidence mean {assessment[COL_SCORE_0_TO_3].mean():.2f}/3. No compliance certification.")
    return assessment

if __name__ == "__main__":
    evaluate_bcbs_239_principles()
