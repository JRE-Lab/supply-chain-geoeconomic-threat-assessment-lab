diff --git a/lab/src/pipeline.py b/lab/src/pipeline.py
new file mode 100644
index 0000000000000000000000000000000000000000..8d8ef575080d199af1f22bcee8377f0b7863fe83
--- /dev/null
+++ b/lab/src/pipeline.py
@@ -0,0 +1,55 @@
+import argparse
+from pathlib import Path
+
+import assess
+import ingest
+import report
+import pandas as pd
+
+
+def run_pipeline(data_dir: Path, output_dir: Path) -> None:
+    output_dir.mkdir(parents=True, exist_ok=True)
+
+    merged_path = output_dir / "merged_data.csv"
+    risk_scores_path = output_dir / "risk_scores.csv"
+    brief_path = output_dir / "brief.md"
+
+    supplier_profile = ingest.build_supplier_profile(data_dir)
+    supplier_profile.to_csv(merged_path, index=False)
+
+    geo_risk = pd.read_csv(data_dir / "geo_risk.csv")
+    scored = assess.score_suppliers(supplier_profile, geo_risk)
+    scored.to_csv(risk_scores_path, index=False)
+
+    brief = report.build_summary(scored)
+    brief_path.write_text(brief, encoding="utf-8")
+
+    print("Pipeline complete.")
+    print(f"- Merged data: {merged_path}")
+    print(f"- Risk scores: {risk_scores_path}")
+    print(f"- Brief: {brief_path}")
+
+
+def main() -> None:
+    parser = argparse.ArgumentParser(
+        description="Run the full supply-chain risk assessment pipeline."
+    )
+    parser.add_argument(
+        "--data-dir",
+        type=Path,
+        default=Path(__file__).resolve().parents[1] / "data",
+        help="Directory containing CSV inputs.",
+    )
+    parser.add_argument(
+        "--output-dir",
+        type=Path,
+        default=Path("outputs"),
+        help="Directory to write pipeline outputs.",
+    )
+    args = parser.parse_args()
+
+    run_pipeline(args.data_dir, args.output_dir)
+
+
+if __name__ == "__main__":
+    main()
