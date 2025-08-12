import pandas as pd

# Load your cleaned data
df = pd.read_csv(r"C:\Users\Dell User\Desktop\Fusarium_Proteomics_Project\Fusarium_Project\cleaned\cleaned_data.csv")

# Extract unique UniProt IDs
protein_ids = df["T: Single Protein IDs"].dropna().unique()

# Save to your 'cleaned' folder inside your project
pd.DataFrame(protein_ids, columns=["UniProt ID"]).to_csv(
    r"C:\Users\Dell User\Desktop\Fusarium_Proteomics_Project\Fusarium_Project\cleaned\unique_uniprot_ids.csv",
    index=False
)

print("✅ Saved unique UniProt IDs to your cleaned folder.")

