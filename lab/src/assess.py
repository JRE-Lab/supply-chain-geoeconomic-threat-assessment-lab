diff --git a/lab/src/assess.py b/lab/src/assess.py
new file mode 100644
index 0000000000000000000000000000000000000000..5f3b7966f516af2aa53e7659548a2d39f071998e
--- /dev/null
+++ b/lab/src/assess.py
@@ -0,0 +1,95 @@
+import argparse
+from pathlib import Path
+
+import numpy as np
+import pandas as pd
+
+WEIGHTS = {
+    "geo_risk": 0.3,
+    "transit_risk": 0.15,
+    "concentration_risk": 0.2,
+    "reliability_risk": 0.15,
+    "sanctions_risk": 0.2,
+}
+
+
+def normalize_series(series: pd.Series) -> pd.Series:
+    min_val = series.min()
+    max_val = series.max()
+    if max_val == min_val:
+        return pd.Series(np.zeros(len(series)), index=series.index)
+    return (series - min_val) / (max_val - min_val)
+
+
+def calculate_geo_risk(geo_risk: pd.DataFrame) -> pd.DataFrame:
+    risk_cols = [
+        "political_risk",
+        "regulatory_risk",
+        "conflict_risk",
+        "currency_risk",
+    ]
+    geo_risk["geo_risk"] = geo_risk[risk_cols].mean(axis=1)
+    return geo_risk[["country", "geo_risk"]]
+
+
+def score_suppliers(merged: pd.DataFrame, geo_risk: pd.DataFrame) -> pd.DataFrame:
+    geo = calculate_geo_risk(geo_risk)
+    scored = merged.merge(geo, on="country", how="left")
+    scored["geo_risk"] = scored["geo_risk"].fillna(scored["geo_risk"].mean())
+
+    scored["concentration_risk"] = normalize_series(scored["concentration_share"])
+    scored["reliability_risk"] = 1 - scored["reliability_score"]
+    scored["transit_risk"] = scored["avg_transit_risk"].fillna(0)
+    scored["sanctions_risk"] = scored["sanctions_risk"].fillna(0)
+
+    weighted_score = (
+        scored["geo_risk"] * WEIGHTS["geo_risk"]
+        + scored["transit_risk"] * WEIGHTS["transit_risk"]
+        + scored["concentration_risk"] * WEIGHTS["concentration_risk"]
+        + scored["reliability_risk"] * WEIGHTS["reliability_risk"]
+        + scored["sanctions_risk"] * WEIGHTS["sanctions_risk"]
+    )
+
+    scored["risk_score"] = (weighted_score * 100).round(1)
+    scored["risk_tier"] = pd.cut(
+        scored["risk_score"],
+        bins=[-np.inf, 33, 66, np.inf],
+        labels=["Low", "Moderate", "High"],
+    )
+    return scored
+
+
+def main() -> None:
+    parser = argparse.ArgumentParser(description="Calculate supplier risk scores.")
+    parser.add_argument(
+        "--merged",
+        type=Path,
+        default=Path("merged_data.csv"),
+        help="Merged supplier dataset from ingest step.",
+    )
+    parser.add_argument(
+        "--geo",
+        type=Path,
+        default=Path(__file__).resolve().parents[1] / "data" / "geo_risk.csv",
+        help="Geo risk dataset.",
+    )
+    parser.add_argument(
+        "--output",
+        type=Path,
+        default=Path("risk_scores.csv"),
+        help="Output CSV path for risk scores.",
+    )
+    args = parser.parse_args()
+
+    merged = pd.read_csv(args.merged)
+    geo_risk = pd.read_csv(args.geo)
+
+    scored = score_suppliers(merged, geo_risk)
+    output_path = args.output
+    output_path.parent.mkdir(parents=True, exist_ok=True)
+    scored.to_csv(output_path, index=False)
+    print(f"Wrote risk scores to {output_path}")
+
+
+if __name__ == "__main__":
+    main()
