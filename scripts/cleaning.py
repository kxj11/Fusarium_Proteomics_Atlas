# Inspecting & Cleaning Proteomics Data
import os
import pandas as pd

# === SETUP ===
base_dir = os.path.dirname(os.path.dirname(__file__))  # Gets project root
data_path = os.path.join(base_dir, "data", "proteomics_data.txt")
cleaned_dir = os.path.join(base_dir, "cleaned")
os.makedirs(cleaned_dir, exist_ok=True)

# === LOAD DATA ===
df = pd.read_csv(data_path, sep="\t", low_memory=False)

# === SEPARATE METADATA + CLEAN DATA ===
metadata_rows = df.iloc[0:4]                      # Store metadata rows separately
df_clean = df.iloc[4:].reset_index(drop=True)     # Real data starts from row 5
df_clean.columns = df_clean.columns.str.strip()   # Clean column names

# Convert values to numeric where possible
for col in df_clean.columns:
    df_clean[col] = pd.to_numeric(df_clean[col], errors='ignore')

# Drop rows with missing protein ID
df_clean = df_clean[df_clean["T: Single Protein IDs"].notna()]

# Drop any columns starting with '#'
columns_to_drop = [col for col in df_clean.columns if str(col).startswith("#")]
df_clean = df_clean.drop(columns=columns_to_drop)

# === SAVE CLEANED DATA ===
cleaned_data_path = os.path.join(cleaned_dir, "cleaned_data.csv")
df_clean.to_csv(cleaned_data_path, index=False)
print("✅ Cleaned data saved to:", cleaned_data_path)

# === BUILD MAPPING TABLE ===
intensity_cols = metadata_rows.columns[:df.shape[1] - 15]  # Exclude metadata columns at the end

mapping_df = pd.DataFrame({
    "Original_Column": intensity_cols,
    "Sample_Code": metadata_rows.iloc[1][intensity_cols].values,
    "Group": metadata_rows.iloc[2][intensity_cols].values,
    "Cultivar_Treatment": metadata_rows.iloc[3][intensity_cols].values
})
mapping_df["TMT_Label"] = ["TMT_" + str(i + 1) for i in range(len(mapping_df))]

# Remove any placeholder groups from mapping
mapping_df = mapping_df[~mapping_df["Group"].str.startswith("#", na=False)]
mapping_df = mapping_df[~mapping_df["Cultivar_Treatment"].str.startswith("#", na=False)]

# === SAVE CLEANED MAPPING TABLE ===
mapping_path = os.path.join(cleaned_dir, "mapping_table.csv")
mapping_df.to_csv(mapping_path, index=False)
print("✅ Mapping table saved to:", mapping_path)
