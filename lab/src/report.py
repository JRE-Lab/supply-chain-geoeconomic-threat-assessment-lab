diff --git a/lab/src/report.py b/lab/src/report.py
new file mode 100644
index 0000000000000000000000000000000000000000..b90539569d80df288dfa7496100a77496571299a
--- /dev/null
+++ b/lab/src/report.py
@@ -0,0 +1,78 @@
+import argparse
+from pathlib import Path
+
+import pandas as pd
+
+
+def build_summary(risk_scores: pd.DataFrame) -> str:
+    top_risks = risk_scores.sort_values("risk_score", ascending=False).head(3)
+    tier_counts = risk_scores["risk_tier"].value_counts().to_dict()
+
+    lines = [
+        "# Supply-Chain & Geoeconomic Threat Assessment Brief",
+        "",
+        "## Executive summary",
+        "",
+        f"* Total suppliers assessed: {len(risk_scores)}",
+        f"* High risk suppliers: {tier_counts.get('High', 0)}",
+        f"* Moderate risk suppliers: {tier_counts.get('Moderate', 0)}",
+        f"* Low risk suppliers: {tier_counts.get('Low', 0)}",
+        "",
+        "## Top risk hotspots",
+    ]
+
+    for _, row in top_risks.iterrows():
+        lines.append(
+            "* "
+            f"**{row['name']}** ({row['country']}, {row['sector']}) - "
+            f"Risk score {row['risk_score']} ({row['risk_tier']})"
+        )
+        lines.append(
+            "  * Key factors: "
+            f"Geo risk {row['geo_risk']:.2f}, "
+            f"Transit {row['transit_risk']:.2f}, "
+            f"Concentration {row['concentration_risk']:.2f}, "
+            f"Sanctions {row['sanctions_risk']}"
+        )
+
+    lines.extend(
+        [
+            "",
+            "## Recommended follow-up",
+            "",
+            "* Validate supplier ownership chains against the latest corporate registries.",
+            "* Cross-check shipping choke points and contingency routing options.",
+            "* Build diversification scenarios for high concentration suppliers.",
+            "* Monitor sanctions and regulatory changes monthly.",
+        ]
+    )
+
+    return "\n".join(lines)
+
+
+def main() -> None:
+    parser = argparse.ArgumentParser(description="Generate a markdown analytic brief.")
+    parser.add_argument(
+        "--risk-scores",
+        type=Path,
+        default=Path("risk_scores.csv"),
+        help="Risk score CSV from assess step.",
+    )
+    parser.add_argument(
+        "--output",
+        type=Path,
+        default=Path("brief.md"),
+        help="Output markdown brief path.",
+    )
+    args = parser.parse_args()
+
+    risk_scores = pd.read_csv(args.risk_scores)
+    report = build_summary(risk_scores)
+    output_path = args.output
+    output_path.parent.mkdir(parents=True, exist_ok=True)
+    output_path.write_text(report, encoding="utf-8")
+    print(f"Wrote brief to {output_path}")
+
+
+if __name__ == "__main__":
+    main()
