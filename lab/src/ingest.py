diff --git a/lab/src/ingest.py b/lab/src/ingest.py
new file mode 100644
index 0000000000000000000000000000000000000000..d45ebe78298edd40cdd5f12ae83a57280f8eb371
--- /dev/null
+++ b/lab/src/ingest.py
@@ -0,0 +1,65 @@
+import argparse
+from pathlib import Path
+
+import pandas as pd
+
+
+def load_csv(data_dir: Path, filename: str) -> pd.DataFrame:
+    path = data_dir / filename
+    if not path.exists():
+        raise FileNotFoundError(f"Missing required data file: {path}")
+    return pd.read_csv(path)
+
+
+def build_supplier_profile(data_dir: Path) -> pd.DataFrame:
+    suppliers = load_csv(data_dir, "suppliers.csv")
+    routes = load_csv(data_dir, "shipping_routes.csv")
+    sanctions = load_csv(data_dir, "sanctions.csv")
+
+    route_risk = (
+        routes.groupby("supplier_id", as_index=False)["transit_risk"]
+        .mean()
+        .rename(columns={"transit_risk": "avg_transit_risk"})
+    )
+
+    suppliers = suppliers.merge(route_risk, on="supplier_id", how="left")
+    suppliers["avg_transit_risk"] = suppliers["avg_transit_risk"].fillna(0)
+
+    sanctions_entities = sanctions["entity"].str.strip().str.lower().tolist()
+    suppliers["sanctions_match"] = suppliers["ownership_parent"].str.strip().str.lower().isin(
+        sanctions_entities
+    )
+    suppliers["sanctions_flag"] = suppliers["sanctions_flag"].astype(int)
+    suppliers["sanctions_risk"] = suppliers["sanctions_flag"].clip(0, 1) | suppliers[
+        "sanctions_match"
+    ]
+    suppliers["sanctions_risk"] = suppliers["sanctions_risk"].astype(int)
+
+    return suppliers
+
+
+def main() -> None:
+    parser = argparse.ArgumentParser(description="Ingest and normalize lab datasets.")
+    parser.add_argument(
+        "--data-dir",
+        type=Path,
+        default=Path(__file__).resolve().parents[1] / "data",
+        help="Directory containing CSV inputs.",
+    )
+    parser.add_argument(
+        "--output",
+        type=Path,
+        default=Path("merged_data.csv"),
+        help="Output CSV path for merged supplier profile.",
+    )
+    args = parser.parse_args()
+
+    supplier_profile = build_supplier_profile(args.data_dir)
+    output_path = args.output
+    output_path.parent.mkdir(parents=True, exist_ok=True)
+    supplier_profile.to_csv(output_path, index=False)
+    print(f"Wrote merged dataset to {output_path}")
+
+
+if __name__ == "__main__":
+    main()
