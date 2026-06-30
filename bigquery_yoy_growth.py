import pandas as pd
from google.cloud import bigquery

client = bigquery.Client(project="project-b7841bf5-9e40-4961-8f0")

print("Connected to BigQuery")

query = """
SELECT
  q.area_fips,
  a.area_title,
  q.year,
  q.qtr,
  q.avg_quarterly_employment,
  q.qtrly_estabs,
  q.avg_wkly_wage,
  q.employment_index,
  q.employer_index,
  q.wage_index
FROM `project-b7841bf5-9e40-4961-8f0.qcew_project.qcew_paychex_proxy_index` q
LEFT JOIN `project-b7841bf5-9e40-4961-8f0.qcew_project.qcew_area_lookup` a
  ON q.area_fips = a.area_fips
WHERE q.year IN (2024, 2025)
AND q.avg_quarterly_employment > 0
  AND q.avg_wkly_wage > 0
  AND a.area_title NOT LIKE 'Unknown%'
"""

df = client.query(query).to_dataframe()

print("Rows pulled from BigQuery:", df.shape)
print(df.head())

df["avg_quarterly_employment"] = pd.to_numeric(
    df["avg_quarterly_employment"],
    errors="coerce"
)

annual = (
    df.groupby(["area_fips", "area_title", "year"], as_index=False)
      .agg(avg_annual_employment=("avg_quarterly_employment", "mean"))
)

print("Annual rows and columns:", annual.shape)
print(annual.head())

pivot = annual.pivot(
    index=["area_fips", "area_title"],
    columns="year",
    values="avg_annual_employment"
).reset_index()

pivot = pivot.rename(columns={
    2024: "employment_2024",
    2025: "employment_2025"
})

print(pivot.head())

pivot["yoy_employment_growth"] = (
    (pivot["employment_2025"] - pivot["employment_2024"]) /
    pivot["employment_2024"]
)

results = pivot[
    (pivot["employment_2025"] > 10000) &
    (pivot["yoy_employment_growth"] > 0.10)
].copy()

print("Results rows and columns:", results.shape)
print(results.head())

results["yoy_employment_growth_pct"] = results["yoy_employment_growth"] * 100

results = results.sort_values("yoy_employment_growth_pct", ascending=False)

results.to_csv(
    "/Users/jordanpearlstone/Downloads/qcew_map_growth_results.csv",
    index=False
)

print("Saved all qualifying areas to Downloads as qcew_map_growth_results.csv")
print("Number of qualifying areas:", len(results))

# to verify that there are only 9 areas that meet the criteria:
print("Total areas in pivot:", len(pivot))

print("Areas with 2025 employment over 10,000:")
print((pivot["employment_2025"] > 10000).sum())

print("Areas with YoY growth over 10%:")
print((pivot["yoy_employment_growth"] > 0.10).sum())

print("Areas with both filters:")
print(((pivot["employment_2025"] > 10000) & (pivot["yoy_employment_growth"] > 0.10)).sum())
