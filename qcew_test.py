import pandas as pd
from pathlib import Path

folder = Path("/Users/jordanpearlstone/Downloads/Quarterly Reports")
files = list(folder.glob("*.csv"))

print(files)
print("Number of files found:", len(files))

cols = [
    "area_fips",
    "own_code",
    "industry_code",
    "year",
    "qtr",
    "qtrly_estabs",
    "month1_emplvl",
    "month2_emplvl",
    "month3_emplvl",
    "avg_wkly_wage",
    "total_qtrly_wages"
]

print("Starting to combine needed columns only...")

df = pd.concat(
    [pd.read_csv(file, usecols=cols, low_memory=False) for file in files],
    ignore_index=True
)

print("Finished combining files")
print("Combined rows and columns:", df.shape)
print(df.head())

df["industry_code"] = df["industry_code"].astype(str)

df_private_total = df[
    (df["own_code"] == 5) &
    (df["industry_code"] == "10")
].copy()

print("Private total rows and columns:", df_private_total.shape)
print(df_private_total.head())

df_private_total["avg_quarterly_employment"] = (
    df_private_total["month1_emplvl"] +
    df_private_total["month2_emplvl"] +
    df_private_total["month3_emplvl"]
) / 3

print(df_private_total[[
    "area_fips",
    "year",
    "qtr",
    "qtrly_estabs",
    "avg_quarterly_employment",
    "avg_wkly_wage"
]].head())

base = df_private_total[
    (df_private_total["year"] == 2019) &
    (df_private_total["qtr"] == 4)
].copy()

print("Base period rows:", base.shape)
print(base.head())

base = base[[
    "area_fips",
    "avg_quarterly_employment",
    "qtrly_estabs",
    "avg_wkly_wage"
]].copy()

base = base.rename(columns={
    "avg_quarterly_employment": "base_employment",
    "qtrly_estabs": "base_employers",
    "avg_wkly_wage": "base_wage"
})

print(base.head())

df_index = df_private_total.merge(base, on="area_fips", how="left")

print("Index rows and columns:", df_index.shape)
print(df_index.head())

df_index["employment_index"] = (
    df_index["avg_quarterly_employment"] / df_index["base_employment"] * 100
)

df_index["employer_index"] = (
    df_index["qtrly_estabs"] / df_index["base_employers"] * 100
)

df_index["wage_index"] = (
    df_index["avg_wkly_wage"] / df_index["base_wage"] * 100
)

print(df_index[[
    "area_fips",
    "year",
    "qtr",
    "employment_index",
    "employer_index",
    "wage_index"
]].head())

output = df_index[[
    "area_fips",
    "year",
    "qtr",
    "avg_quarterly_employment",
    "qtrly_estabs",
    "avg_wkly_wage",
    "employment_index",
    "employer_index",
    "wage_index"
]].copy()

print(output.head())
print("Final rows and columns:", output.shape)

output.to_csv("/Users/jordanpearlstone/Downloads/qcew_paychex_proxy_index.csv", index=False)

print("Saved file to Downloads as qcew_paychex_proxy_index.csv")
